# written 2022-01-12 by mza
# based on indoor_temp_hum.py
# last updated 2022-12-03 by mza

# to install on a circuitpython device:
# rsync -av *.py /media/circuitpython/
# cp -a outdoor_temp_hum.py /media/circuitpython/code.py
# cd ~/build/adafruit-circuitpython/bundle/lib
# rsync -r adafruit_datetime.mpy adafruit_minimqtt adafruit_sdcard.mpy adafruit_sht31d.mpy simpleio.mpy adafruit_esp32spi adafruit_register neopixel.mpy adafruit_io adafruit_requests.mpy adafruit_bus_device /media/circuitpython/lib/

import sys
import time
import atexit
import board
import busio
import simpleio
import microsd_adafruit
import neopixel_adafruit
import sht31d_adafruit
import airlift
import gps_adafruit
from DebugInfoWarningError24 import debug, info, warning, error, debug2, debug3, set_verbosity, create_new_logfile_with_string_embedded, flush
import generic

DESIRED_NUMBER_OF_SECONDS_BETWEEN_POSTING = 60
NUMBER_OF_SECONDS_TO_WAIT_BEFORE_FORCING_RESET = 5 * DESIRED_NUMBER_OF_SECONDS_BETWEEN_POSTING

header_string = "date/time"
mydir = "/logs"
board_id = board.board_id
info("we are " + board_id)
if 'adafruit_qtpy_esp32s2'==board_id: # sht31 on qtpy esp32-s2
	my_wifi_name = "outdoor"
	my_adafruit_io_prefix = "outdoor"
	FEATHER_ESP32S2 = True
	use_pwm_status_leds = False
	should_use_sdcard = False
	should_use_RTC = False
	should_use_gps = False
	N = 32
	delay_between_acquisitions = 1.7
	gps_delay_in_ms = 2000
	#delay_between_posting_and_next_acquisition = 1.0
	should_use_airlift = True
	use_built_in_wifi = True
	should_use_display = False
else:
	error("what kind of board am I?")

def print_header():
	info("" + header_string)

def print_compact(string):
	date = ""
	if ""==date:
		try:
			import time
			date = time.strftime("%Y-%m-%d+%X")
		except KeyboardInterrupt:
			raise
		except:
			pass
	if ""==date and RTC_is_available:
		try:
			import pcf8523_adafruit
			date = pcf8523_adafruit.get_timestring1()
		except KeyboardInterrupt:
			raise
		except:
			pass
	if ""==date and gps_is_available:
		try:
			import gps_adafruit
			date = gps_adafruit.get_time()
		except KeyboardInterrupt:
			raise
		except:
			pass
	info("%s%s" % (date, string))

def print_header():
	info("" + header_string)

def main():
	generic.start_uptime()
	global header_string
	if use_pwm_status_leds:
		generic.setup_status_leds(red_pin=board.A2, green_pin=board.D9, blue_pin=board.A3)
		generic.set_status_led_color([1.0, 1.0, 1.0])
	if FEATHER_ESP32S2: # for feather esp32-s2 to turn on power to i2c bus:
		simpleio.DigitalOut(board.D7, value=0)
	global i2c
	try:
		#i2c = board.I2C
		#string = "using I2C (builtin)"
		raise
	except KeyboardInterrupt:
		raise
	except:
		try:
			i2c = busio.I2C(board.SCL1, board.SDA1)
			string = "using I2C1 "
		except KeyboardInterrupt:
			raise
		except:
			#i2c = busio.I2C(board.SCL, board.SDA)
			i2c = board.I2C()
			string = "using I2C0 "
	info(string)
	#i2c.try_lock()
	#i2c_list = i2c.scan()
	#i2c.unlock()
	#info(string + str(i2c_list))
	global spi
	try:
		spi = board.SPI
		info("builtin SPI (1)")
	except KeyboardInterrupt:
		raise
	except:
		spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
		info("builtin SPI (2)")
	#global uart
	#uart = busio.UART(board.TX, board.RX, baudrate=9600, timeout=10)
	prohibited_addresses = []
	global RTC_is_available
	if should_use_RTC:
		try:
			i2c_address = pcf8523_adafruit.setup(i2c)
			prohibited_addresses.append(i2c_address)
			RTC_is_available = True
		except KeyboardInterrupt:
			raise
		except:
			RTC_is_available = False
	else:
		RTC_is_available = False
	global sdcard_is_available
	global mydir
	if should_use_sdcard:
		sdcard_is_available = microsd_adafruit.setup_sdcard_for_logging_data(spi, board.D10, mydir) # D10 = adalogger featherwing
	else:
		sdcard_is_available = False
	if not sdcard_is_available:
		mydir = ""
	if should_use_sdcard:
		if RTC_is_available:
			create_new_logfile_with_string_embedded(mydir, my_wifi_name, pcf8523_adafruit.get_timestring2())
		else:
			create_new_logfile_with_string_embedded(mydir, my_wifi_name)
	global gps_is_available
	if should_use_gps:
		if 1:
			gps_adafruit.setup_uart(uart, N, gps_delay_in_ms)
		else:
			gps_adafruit.setup_i2c(i2c, N, gps_delay_in_ms)
		gps_is_available = True
		header_string += gps_adafruit.header_string()
	else:
		gps_is_available = False
	global neopixel_is_available
	try:
		neopixel_is_available = neopixel_adafruit.setup_neopixel()
	except KeyboardInterrupt:
		raise
	except:
		warning("error setting up neopixel")
	global sht31d_is_available
	try:
		i2c_address = sht31d_adafruit.setup(i2c, N)
		prohibited_addresses.append(i2c_address)
		header_string += ", sht31d-%RH, sht31d-C"
		sht31d_is_available = True
	except:
		error("sht31d not found")
		sys.exit(1)
		sht31d_is_available = False
	#info("prohibited i2c addresses: " + str(prohibited_addresses)) # disallow treating any devices already discovered as pct2075s
	if use_pwm_status_leds:
		generic.set_status_led_color([0.5, 0.5, 0.5])
	global airlift_is_available
	airlift_is_available = False
	if should_use_airlift:
		if use_built_in_wifi:
			airlift_is_available = airlift.setup_wifi(my_wifi_name)
		else:
			airlift_is_available = airlift.setup_airlift(my_wifi_name, spi, board.D13, board.D11, board.D12)
	if airlift_is_available:
		header_string += ", RSSI-dB"
		airlift.setup_feed(my_adafruit_io_prefix + "-temp")
		airlift.setup_feed(my_adafruit_io_prefix + "-hum")
		#airlift.setup_feed(my_adafruit_io_prefix + "-pressure")
		airlift.setup_feed(my_adafruit_io_prefix + "-rssi")
		#airlift.setup_feed("indoor-altitude")
		#airlift.setup_feed("indoor-gas")
	if 0:
		if airlift_is_available:
			airlift.update_time_from_server()
	#gnuplot> set key autotitle columnheader
	#gnuplot> set style data lines
	#gnuplot> plot for [i=1:14] "solar_water_heater.log" using 0:i
	print_header()
	global i
	i = 0
	loop()
	info("sht31d no longer available; cannot continue")

def loop():
	global i
	last_good_post_time = generic.get_uptime()
	global delay_between_acquisitions
	while sht31d_adafruit.test_if_present():
		neopixel_adafruit.set_color(255, 0, 0)
		if use_pwm_status_leds:
			generic.set_status_led_color([1, 0, 0])
		string = ""
		if gps_is_available:
			string += gps_adafruit.measure_string()
		if sht31d_is_available:
			#info("sht31d")
			string += sht31d_adafruit.measure_string()
		if airlift_is_available:
			string += airlift.measure_string()
		print_compact(string)
		flush()
		neopixel_adafruit.set_color(0, 255, 0)
		if use_pwm_status_leds:
			generic.set_status_led_color([0, 1, 0])
		i += 1
		if 0==i%N:
			delay_between_acquisitions = generic.adjust_delay_for_desired_loop_time(delay_between_acquisitions, N, DESIRED_NUMBER_OF_SECONDS_BETWEEN_POSTING)
			if sht31d_is_available:
				sht31d_adafruit.show_average_values()
				if airlift_is_available:
					try:
						airlift.post_data(my_adafruit_io_prefix + "-temp", sht31d_adafruit.get_average_values()[1])
						airlift.post_data(my_adafruit_io_prefix + "-hum",  sht31d_adafruit.get_average_values()[0])
						last_good_post_time = generic.get_uptime()
					except KeyboardInterrupt:
						raise
					except:
						warning("couldn't post data for sht31d")
			if airlift_is_available:
				airlift.show_average_values()
				try:
					airlift.post_data(my_adafruit_io_prefix + "-rssi", airlift.get_average_values()[0])
					#last_good_post_time = generic.get_uptime()
				except (KeyboardInterrupt, ReloadException):
					raise
				except:
					warning("couldn't post data for rssi")
				current_time = generic.get_uptime()
				time_since_last_good_post = current_time - last_good_post_time
				info("time since last good post: " + str(time_since_last_good_post) + " s")
				if NUMBER_OF_SECONDS_TO_WAIT_BEFORE_FORCING_RESET < time_since_last_good_post:
					error("too long since a post operation succeeded")
					generic.reset()
			info("waiting...")
			#time.sleep(delay_between_posting_and_next_acquisition)
		neopixel_adafruit.set_color(0, 0, 255)
		if use_pwm_status_leds:
			generic.set_status_led_color([0, 0, 1])
		if airlift_is_available:
			if 0==i%86300:
				airlift.update_time_from_server()
		time.sleep(delay_between_acquisitions)

if __name__ == "__main__":
	atexit.register(generic.reset)
	try:
		main()
	except KeyboardInterrupt:
		generic.keyboard_interrupt_exception_handler()
	except ReloadException:
		generic.reload_exception_handler()
	info("leaving program...")
	flush()
	generic.reset()

