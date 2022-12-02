# written 2022-10-29 by mza
# based on neopixel_clockface.py
# last updated 2022-12-01 by mza

# to install:
# cd lib
# rsync -r adafruit_lc709203f.mpy adafruit_as7341.mpy neopixel.mpy adafruit_minimqtt simpleio.mpy adafruit_esp32spi adafruit_register adafruit_io adafruit_requests.mpy adafruit_bus_device /media/mza/CIRCUITPY/lib/
# cd ..
# rsync -av *.py /media/mza/CIRCUITPY/
# cp -a roofDAQ2.py /media/mza/CIRCUITPY/code.py; sync

import time
import re
import board
import busio
import neopixel_adafruit
import as7341_adafruit
import lc709203f_adafruit
import airlift
import generic
from DebugInfoWarningError24 import debug, info, warning, error, debug2, debug3, set_verbosity, create_new_logfile_with_string_embedded, flush

# drained a 400 mAh battery in about 4 hours, so draws ~100 mA (at night)
# drained a 4400 mAh battery in 64 hours, so draws ~68.75 mA (0.6W solar panel connected)
# assuming fully sunny days, the solar panel got ~12 hours @ 110 mA, so current draw is somewhere around 90 mA
# ammeter says 30-80 mA while collecting data, and then 50-80 mA while posting data
# if we do the should_power_down_wifi_when_not_needed mode, the current draw is 80-90 mA while wifiing but 20-30 mA otherwise

my_wifi_name = "roof2"
my_adafruit_io_prefix = "roof2"
delay_between_acquisitions = 1.5
N = 32 # average this many sensor readings before acting on it
should_use_RTC = False
should_power_down_wifi_when_not_needed = False
#NUMBER_OF_SECONDS_TO_WAIT_BEFORE_FORCING_RESET = 3600
DESIRED_NUMBER_OF_SECONDS_BETWEEN_POSTING = 60
NUMBER_OF_SECONDS_TO_WAIT_BEFORE_FORCING_RESET = 5 * DESIRED_NUMBER_OF_SECONDS_BETWEEN_POSTING
should_use_fuel_gauge = True

eta = 1.0/512.0

def setup():
	generic.start_uptime()
	global neopixel_is_available
	neopixel_is_available = False
	try:
		neopixel_is_available = neopixel_adafruit.setup_neopixel()
	except (KeyboardInterrupt, ReloadException):
		raise
	except:
		warning("error setting up neopixel")
	if neopixel_is_available:
		neopixel_adafruit.set_color(255, 255, 255)
	header_string = ""
	global i2c
	try:
		i2c = busio.I2C(board.SCL1, board.SDA1)
		string = "using I2C1 "
	except (KeyboardInterrupt, ReloadException):
		raise
	except:
		#i2c = busio.I2C(board.SCL, board.SDA)
		i2c = board.I2C()
		string = "using I2C0 "
	info(string)
	if neopixel_is_available:
		neopixel_adafruit.set_color(255, 255, 0)
	global as7341_is_available
	as7341_is_available = False
	try:
		i2c_address = as7341_adafruit.setup(i2c, N)
		as7341_is_available = True
		header_string += ", as7341-415nm, as7341-445nm, as7341-480nm, as7341-515nm, as7341-555nm, as7341-590nm, as7341-630nm, as7341-680nm, as7341-clear, as7341-nir"
	except (KeyboardInterrupt, ReloadException):
		raise
	except:
		warning("as7341 not found")
	if neopixel_is_available:
		neopixel_adafruit.set_color(0, 255, 255)
	global RTC_is_available
	RTC_is_available = False
	if should_use_RTC:
		try:
			#i2c_address = pcf8523_adafruit.setup(i2c)
			i2c_address = ds3231_adafruit.setup(i2c)
			RTC_is_available = True
		except (KeyboardInterrupt, ReloadException):
			raise
		except:
			RTC_is_available = False
	if RTC_is_available:
		string = ds3231_adafruit.get_timestring2()
		info(string)
	global fuel_gauge_is_available
	fuel_gauge_is_available = False
	if neopixel_is_available:
		neopixel_adafruit.set_color(255, 0, 255)
	global airlift_is_available
	airlift_is_available = airlift.setup_wifi(my_wifi_name)
	if 0:
		if airlift_is_available:
			airlift.update_time_from_server()
	if neopixel_is_available:
		neopixel_adafruit.set_color(0, 127, 127)
	if airlift_is_available:
		header_string += ", rssi-dB"
	if should_use_fuel_gauge:
		lc709203f_adafruit.setup(i2c, N)
		header_string += ", batt-V, batt-%"
		fuel_gauge_is_available = True
	if airlift_is_available:
		feed_suffixes = [ "415nm", "445nm", "480nm", "515nm", "555nm", "590nm", "630nm", "680nm", "clear", "nir", "rssi", "batt" ]
		feed_names = []
		for feed_suffix in feed_suffixes:
			feed_names.append(my_adafruit_io_prefix + "-" + feed_suffix)
		airlift.setup_feeds(feed_names)
	if neopixel_is_available:
		neopixel_adafruit.set_color(127, 127, 127)
	airlift.show_network_status()
	global last_good_post_time
	last_good_post_time = generic.get_uptime()
	info(header_string)

def loop():
	global delay_between_acquisitions
	global last_good_post_time
	global airlift_is_available
	global n
	string = ""
	if neopixel_is_available:
		neopixel_adafruit.set_color(255, 0, 0)
	if as7341_is_available:
		string += as7341_adafruit.measure_string()
		as7341_adafruit.get_values()
	if airlift_is_available:
		string += airlift.measure_string()
	if fuel_gauge_is_available:
		string += lc709203f_adafruit.measure_string()
	info(string)
	n += 1
	if 0==n%N:
		if neopixel_is_available:
			neopixel_adafruit.set_color(0, 255, 0)
		delay_between_acquisitions = generic.adjust_delay_for_desired_loop_time(delay_between_acquisitions, N, DESIRED_NUMBER_OF_SECONDS_BETWEEN_POSTING)
		if should_power_down_wifi_when_not_needed and not airlift_is_available:
			airlift_is_available = True
			airlift.turn_on_wifi()
			airlift.get_values()
		if as7341_is_available:
			as7341_adafruit.show_average_values()
			if airlift_is_available:
				try:
					airlift.post_data(my_adafruit_io_prefix + "-415nm", as7341_adafruit.get_average_values()[0])
					airlift.post_data(my_adafruit_io_prefix + "-445nm", as7341_adafruit.get_average_values()[1])
					airlift.post_data(my_adafruit_io_prefix + "-480nm", as7341_adafruit.get_average_values()[2])
					airlift.post_data(my_adafruit_io_prefix + "-515nm", as7341_adafruit.get_average_values()[3])
					airlift.post_data(my_adafruit_io_prefix + "-555nm", as7341_adafruit.get_average_values()[4])
					airlift.post_data(my_adafruit_io_prefix + "-590nm", as7341_adafruit.get_average_values()[5])
					airlift.post_data(my_adafruit_io_prefix + "-630nm", as7341_adafruit.get_average_values()[6])
					airlift.post_data(my_adafruit_io_prefix + "-680nm", as7341_adafruit.get_average_values()[7])
					airlift.post_data(my_adafruit_io_prefix + "-clear", as7341_adafruit.get_average_values()[8])
					airlift.post_data(my_adafruit_io_prefix + "-nir", as7341_adafruit.get_average_values()[9])
					last_good_post_time = generic.get_uptime()
				except (KeyboardInterrupt, ReloadException):
					raise
				except:
					warning("couldn't post data for as7341")
		if airlift_is_available:
			airlift.show_average_values()
			try:
				airlift.post_data(my_adafruit_io_prefix + "-rssi", airlift.get_average_values()[0])
				#last_good_post_time = generic.get_uptime()
			except (KeyboardInterrupt, ReloadException):
				raise
			except:
				warning("couldn't post data for rssi")
			#debug("last good post time: " + str(last_good_post_time) + " s")
			current_time = generic.get_uptime()
			time_since_last_good_post = current_time - last_good_post_time
			info("time since last good post: " + str(time_since_last_good_post) + " s")
			if NUMBER_OF_SECONDS_TO_WAIT_BEFORE_FORCING_RESET < time_since_last_good_post:
				error("too long since a post operation succeeded")
				generic.reset()
		if fuel_gauge_is_available:
			#info(fuel_gauge.power_mode)
			lc709203f_adafruit.show_average_values()
			#info("battery: " + str() + " V (" + str(fuel_gauge.cell_percent) + "%)")
			if airlift_is_available:
				try:
					cell_voltage = generic.fround(lc709203f_adafruit.get_average_values()[0], 0.001)
					airlift.post_data(my_adafruit_io_prefix + "-batt", cell_voltage)
				except (KeyboardInterrupt, ReloadException):
					raise
				except:
					warning("couldn't post data for batt")
		if should_power_down_wifi_when_not_needed:
			airlift_is_available = False
			airlift.get_values()
			airlift.turn_off_wifi()
	if neopixel_is_available:
		neopixel_adafruit.set_color(0, 0, 255)
	#parse_RTC()
	time.sleep(delay_between_acquisitions)

if __name__ == "__main__":
	set_verbosity(4)
	setup()
	n = 0
	while True:
		loop()

