#!/usr/bin/env python3

# written 2021-04-21 by mza
# updated from indoor_temp_hum.py
# last updated 2022-08-30 by mza

# to install on a circuitpython device:
# rsync -r *.py /media/circuitpython/
# cp -a temperature_log_and_graph.py /media/circuitpython/code.py
# ln -s ~/build/adafruit-circuitpython/bundle/lib
# cd lib
# rsync -av adafruit_minimqtt adafruit_display_text adafruit_esp32spi adafruit_register adafruit_pcf8523.mpy adafruit_pct2075.mpy adafruit_displayio_sh1107.mpy neopixel.mpy adafruit_rgbled.mpy adafruit_requests.mpy adafruit_sdcard.mpy simpleio.mpy adafruit_io /media/circuitpython/lib/
# sync

import sys
import time
import atexit
import board
import busio
import pct2075_adafruit
import airlift
try:
	import adafruit_dotstar as dotstar
except:
	pass
import microsd_adafruit
import neopixel_adafruit
import pcf8523_adafruit
from DebugInfoWarningError24 import debug, info, warning, error, debug2, debug3, set_verbosity, create_new_logfile_with_string_embedded, flush
import generic
import display_adafruit

MIN_TEMP_TO_PLOT = 20.0
MAX_TEMP_TO_PLOT = 80.0

intensity = 8 # brightness of plotted data on dotstar display
board_id = board.board_id
info("we are " + board_id)
if 'sparkfun_samd51_thing_plus'==board_id: # pct2075
	my_wifi_name = "heater"
	N = 32
	desired_loop_time = 60.0
	delay_between_acquisitions = 1.5
	gps_delay_in_ms = 2000
	delay_between_posting_and_next_acquisition = 1.0
	should_use_airlift = True
	use_built_in_wifi = True
	should_use_display = True
	use_built_in_display = False
	use_pwm_status_leds = False
	gps_is_available = False
	battery_monitor_is_available = False
else:
	error("what kind of board am I?")

if 1:
	feed = "heater"
	should_use_dotstar_matrix = False
	should_use_matrix_backpack = False
	should_use_alphanumeric_backpack = False
	should_use_sh1107_oled_display = True
	should_use_ssd1327_oled_display = False
	should_use_sdcard = False
	should_use_RTC = False
	should_plot_temperatures = True
elif 1:
	feed = "test"
	offset_t = 25.0 # min temp we care to plot
	max_t = 28.0 # max temp we care to plot
	N = 13 # number of samples to average over
	delay = 1.0 # number of seconds between samples
	should_use_dotstar_matrix = False
	should_use_matrix_backpack = False
	should_use_alphanumeric_backpack = False
	should_use_sh1107_oled_display = True
	should_use_ssd1327_oled_display = False
	should_use_sdcard = False
	should_use_RTC = False
	should_plot_temperatures = False
else:
	feed = "test"
	offset_t = 25.0 # min temp we care to plot
	max_t = 28.0 # max temp we care to plot
	N = 1*28 # number of samples to average over
	delay = 1.0 # number of seconds between samples
	should_use_airlift = False
	should_use_dotstar_matrix = False
	should_use_matrix_backpack = True
	should_use_alphanumeric_backpack = True
	should_use_sh1107_oled_display = False
	should_use_ssd1327_oled_display = True
	should_use_sdcard = True
	should_use_RTC = True
	should_plot_temperatures = False

temperature_sensors = []
header_string = "heater"
temperature = 0
dirname = "/logs"

def print_header():
	info("#" + header_string)

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

def main():
#	try:
#		displayio.release_displays()
#	except:
#		pass
	global neopixel_is_available
	try:
		neopixel_is_available = neopixel_adafruit.setup_neopixel()
	except:
		error("error setting up neopixel")
		neopixel_is_available = False
	if neopixel_is_available:
		neopixel_adafruit.set_color(127, 127, 127)
	global dotstar_matrix_available
	if should_use_dotstar_matrix:
		dotstar_matrix_available = display_adafruit.setup_dotstar_matrix(False)
	else:
		dotstar_matrix_available = False
	global i2c
	try:
		i2c = busio.I2C(board.SCL1, board.SDA1)
		info("using I2C1")
	except KeyboardInterrupt:
		raise
	except:
		try:
			i2c = busio.I2C(board.SCL, board.SDA)
		except KeyboardInterrupt:
			raise
		except:
			import displayio
			displayio.release_displays()
			i2c = busio.I2C(board.SCL, board.SDA)
		info("using I2C0")
	prohibited_addresses = []
	global display_is_available
	if should_use_ssd1327_oled_display:
		display_is_available = display_adafruit.setup_i2c_oled_display_ssd1327(i2c, 0x3d)
		if display_is_available:
			prohibited_addresses.append(0x3d)
	if should_use_sh1107_oled_display:
		display_is_available = display_adafruit.setup_i2c_oled_display_sh1107(i2c, 0x3c)
		if display_is_available:
			prohibited_addresses.append(0x3c)
	global matrix_backpack_available
	if should_use_matrix_backpack:
		try:
			matrix_backpack_available = display_adafruit.setup_matrix_backpack(i2c)
			if matrix_backpack_available:
				prohibited_addresses.append(0x70)
		except:
			error("can't find matrix backpack (i2c address 0x70)")
			matrix_backpack_available = False
	else:
		matrix_backpack_available = False
	global alphanumeric_backpack_available
	if should_use_alphanumeric_backpack:
		alphanumeric_backpack_available = display_adafruit.setup_alphanumeric_backpack(i2c, 0x77)
	else:
		alphanumeric_backpack_available = False
	if alphanumeric_backpack_available:
		prohibited_addresses.append(0x77)
	if display_is_available:
		display_adafruit.setup_for_n_m_plots(1, 1, [["water heater", "temperature"]])
		display_adafruit.refresh()
	global RTC_is_available
	if should_use_RTC:
		RTC_is_available = pcf8523_adafruit.setup(i2c)
		if RTC_is_available:
			prohibited_addresses.append(RTC_is_available)
	else:
		RTC_is_available = False
	#print(str(prohibited_addresses))
	global pct2075_is_available
	try:
		pct2075_adafruit.setup(i2c, prohibited_addresses, N)
		pct2075_is_available = True
	except:
		error("can't find any temperature sensors on i2c bus")
		pct2075_is_available = False
	global spi
	spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
	global airlift_is_available
	if should_use_airlift:
		airlift_is_available = airlift.setup_airlift(feed, spi, board.D13, board.D11, board.D12)
		#airlift_is_available = airlift.setup_airlift(feed, spi, board.ESP_CS, board.ESP_BUSY, board.ESP_RESET)
	else:
		airlift_is_available = False
	global header_string
	if airlift_is_available:
		airlift.setup_feed(feed)
		header_string += ", RSSI"
	if 0:
		print("fetching old data from feed...")
		global heater
		heater = airlift.get_all_data(MAX_COLUMNS_TO_PLOT)
	global sdcard_is_available
	global dirname
	if should_use_sdcard:
		sdcard_is_available = microsd_adafruit.setup_sdcard_for_logging_data(spi, board.D5, dirname)
		#sdcard_is_available = microsd_adafruit.setup_sdcard_for_logging_data(spi, board.SD_CS, dirname)
	else:
		sdcard_is_available = False
		dirname = ""
	if RTC_is_available:
		create_new_logfile_with_string_embedded(dirname, "heater", pcf8523_adafruit.get_timestring2())
	else:
		create_new_logfile_with_string_embedded(dirname, "heater")
	print_header()
	loop()
	error("pct2075 is no longer available; cannot continue")
	if neopixel_is_available:
		neopixel_adafruit.set_color(0, 255, 255)

def loop():
	if display_is_available:
		plot_width = display_adafruit.plot_width
	else:
		plot_width = 128
	heater = [ -40.0 for i in range(plot_width) ]
	laundry_room = [ -40.0 for i in range(plot_width) ]
	generic.get_uptime()
	global delay_between_acquisitions
	i = 0
	while pct2075_adafruit.test_if_present():
		neopixel_adafruit.set_color(255, 0, 0)
		if use_pwm_status_leds:
			generic.set_status_led_color([1, 0, 0])
		string = ""
		if gps_is_available:
			string += gps_adafruit.measure_string()
		if pct2075_is_available:
			string += pct2075_adafruit.measure_string()
		if airlift_is_available:
			string += airlift.measure_string()
		if battery_monitor_is_available:
			string += generic.get_battery_percentage()
		#display_adafruit.update_temperature_display_on_alphanumeric_backpack(temperature)
		print_compact(string)
		flush()
		neopixel_adafruit.set_color(0, 255, 0)
		if use_pwm_status_leds:
			generic.set_status_led_color([0, 1, 0])
		i += 1
		if 0==i%N:
			if pct2075_is_available:
				pct2075_adafruit.show_average_values()
				heater.append((pct2075_adafruit.get_average_values()[0] - MIN_TEMP_TO_PLOT) / (MAX_TEMP_TO_PLOT-MIN_TEMP_TO_PLOT))
				heater.pop(0)
				laundry_room.append((pct2075_adafruit.get_average_values()[1] - MIN_TEMP_TO_PLOT) / (MAX_TEMP_TO_PLOT-MIN_TEMP_TO_PLOT))
				laundry_room.pop(0)
				#print(str(heater))
				#print(str(laundry_room))
				display_adafruit.update_plot(0, [heater, laundry_room])
				display_adafruit.refresh()
				if airlift_is_available:
					try:
						airlift.post_data(my_wifi_name + "", pct2075_adafruit.get_average_values()[0])
					except KeyboardInterrupt:
						raise
					except:
						warning("couldn't post data for pct2075")
			if dotstar_matrix_available:
				display_adafruit.update_temperature_display_on_dotstar_matrix()
			if matrix_backpack_available:
				display_adafruit.update_temperature_display_on_matrix_backpack()
			info("waiting...")
			time.sleep(delay_between_posting_and_next_acquisition)
			delay_between_acquisitions = generic.adjust_delay_for_desired_loop_time(delay_between_acquisitions, N, desired_loop_time)
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

