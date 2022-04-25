#!/usr/bin/env python3

# written 2022-04-23 by mza
# based on temperature_log_and_graph.py
# last updated 2022-04-24 by mza

# to install on a circuitpython device:
# rsync -av *.py /media/mza/CIRCUITPY/; cp -a weather_station_portal.py /media/mza/CIRCUITPY/code.py ; sync
# ln -s ~/build/adafruit-circuitpython/bundle/lib
# cd lib
# rsync -av microcontroller adafruit_display_text adafruit_esp32spi adafruit_register neopixel.mpy adafruit_rgbled.mpy adafruit_requests.mpy adafruit_sdcard.mpy simpleio.mpy adafruit_io /media/circuitpython/lib/
# sync

import time
import sys
import atexit
import board
import busio
import displayio
import airlift

import microsd_adafruit
import neopixel_adafruit
try:
	from DebugInfoWarningError24 import debug, info, warning, error, debug2, debug3, set_verbosity, create_new_logfile_with_string_embedded, flush
except:
	print("can't find DebugInfoWarningError24.py")
	sys.exit(0)
import generic
import display_adafruit
#import adafruit_touchscreen

if 1:
	feed = "scoopy-boops"
	offset_t = 25.0 # min temp we care to plot
	max_t = 75.0 # max temp we care to plot
	N = 5*60 # number of samples to average over
	delay = 1.0 # number of seconds between samples
	#should_use_airlift = True
	should_use_airlift = False
	should_use_hx8357_lcd = True
	should_use_sdcard = True
	should_use_RTC = False
	should_plot_temperatures = True

temperature_sensors = []
header_string = "scoopy-boops"
temperature = 0
dirname = "/logs"
loop_counter = 0
MAX_COLUMNS_TO_PLOT = 128
#temperatures_to_plot = [ -40.0 for a in range(MAX_COLUMNS_TO_PLOT) ]

def setup_temperature_sensor(i2c, address):
	#i2c.deinit()
	global temperature_sensors
	try:
		pct = adafruit_pct2075.PCT2075(i2c, address=address)
		pct.temperature
		temperature_sensors.append(pct)
	except:
		raise
	return 1

def setup_temperature_sensors(i2c):
	global header_string
	count = 0
	#for address in [0x37, 0x36, 0x35, 0x2f, 0x2e, 0x2d, 0x2c, 0x2b, 0x2a, 0x29, 0x28, 0x77, 0x76, 0x75, 0x74, 0x73, 0x72, 0x71, 0x70, 0x4f, 0x4e, 0x4d, 0x4c, 0x4b, 0x4a, 0x49, 0x48]:
	for address in [0x37, 0x36, 0x35, 0x2f, 0x2e, 0x2d, 0x2c, 0x2b, 0x2a, 0x29, 0x28, 0x76, 0x75, 0x74, 0x73, 0x72, 0x4f, 0x4e, 0x4d, 0x4c, 0x4b, 0x4a, 0x49, 0x48]: # omit 0x70 and 0x71 and 0x77
		try:
			count += setup_temperature_sensor(i2c, address)
			if 1!=count:
				header_string += ", other" + str(count)
		except:
			pass
	if 0==count:
		error("pct2075 not present (any i2c address)")
	else:
		info("found " + str(count) + " temperature sensor(s)")
	return count

def print_header():
	info("#" + header_string)

def measure():
	result = []
	for each in temperature_sensors:
		try:
			result.append(each.temperature)
		except:
			pass
	return result

def measure_string():
	global temperature
	result = measure()
	#string = ", ".join(result)
	temperature = result.pop(0)
	string = "%.1f" % temperature
	for each in result:
		string += ", %.1f" % each
	return string

def print_compact():
	try:
		date = time.strftime("%Y-%m-%d+%X, ")
	except:
		try:
			date = pcf8523_adafruit.get_timestring1() + ", "
		except:
			date = ""
	string = measure_string()
	info("%s%s" % (date, string))

def test_if_present():
	try:
		temperature_sensors[0].temperature
	except:
		return False
	return True

def loop():
	print("loop(" + str(loop_counter) + ")")
	#display_adafruit.update_four_plots(loop_counter)
	time.sleep(1.0)
	lcm4 = loop_counter%4
	if 0==lcm4:
		myarray_a = [ -0.15 + 1.7 * i/display_adafruit.plot_width for i in range(display_adafruit.plot_width) ]
		myarray_b = [ 1.15  - 2.1 * i/display_adafruit.plot_width for i in range(display_adafruit.plot_width) ]
		display_adafruit.update_plot(0, [myarray_a, myarray_b])
	elif 1==lcm4:
		myarray_a = [ 0.10 + 0.5*i/display_adafruit.plot_height for i in range(display_adafruit.plot_width) ]
		myarray_b = [ 0.15 + 0.4*i/display_adafruit.plot_width for i in range(display_adafruit.plot_width) ]
		display_adafruit.update_plot(1, [myarray_a, myarray_b])
	elif 2==lcm4:
		myarray_a = [ 0.1 + 0.5*i/display_adafruit.plot_height for i in range(display_adafruit.plot_width) ]
		display_adafruit.update_plot(2, [myarray_a])
	else:
		myarray_a = [ 0.15 + 0.4*i/display_adafruit.plot_width for i in range(display_adafruit.plot_width) ]
		myarray_b = [ 0.55 - 0.1 * i/display_adafruit.plot_height for i in range(display_adafruit.plot_width) ]
		myarray_c = [ 0.19 + 0.3*i/display_adafruit.plot_height for i in range(display_adafruit.plot_width) ]
		myarray_d = [ 0.12 + 0.2*i/display_adafruit.plot_width for i in range(display_adafruit.plot_width) ]
		display_adafruit.update_plot(3, [myarray_a, myarray_b, myarray_c, myarray_d])
	flush()

def main():
#	try:
#		displayio.release_displays() # this is what stops terminalio from functioning
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
	global i2c
	try:
		i2c = busio.I2C(board.SCL1, board.SDA1)
		info("using I2C1")
	except:
		i2c = busio.I2C(board.SCL, board.SDA)
		info("using I2C0")
#	try:
#		setup_temperature_sensors(i2c)
#	except:
#		error("can't find any temperature sensors on i2c bus")
	global display_is_available
	if should_use_hx8357_lcd:
		display_is_available = display_adafruit.setup_builtin_lcd_hx8357()
	global RTC_is_available
	if should_use_RTC:
		RTC_is_available = pcf8523_adafruit.setup(i2c)
	else:
		RTC_is_available = False
	global spi
	spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
	global airlift_is_available
	if should_use_airlift:
		airlift_is_available = airlift.setup_airlift(feed, spi, board.ESP_CS, board.ESP_BUSY, board.ESP_RESET)
	else:
		airlift_is_available = False
	if airlift_is_available:
		airlift.setup_feed(feed)
	if 0:
		print("fetching old data from feed...")
		global temperatures_to_plot
		temperatures_to_plot = airlift.get_all_data(MAX_COLUMNS_TO_PLOT)
	global sdcard_is_available
	global dirname
	if should_use_sdcard:
		sdcard_is_available = microsd_adafruit.setup_sdcard_for_logging_data(spi, board.SD_CS, dirname)
	else:
		sdcard_is_available = False
		dirname = "/"
	if RTC_is_available:
		create_new_logfile_with_string_embedded(dirname, "weather_station", pcf8523_adafruit.get_timestring2())
	else:
		create_new_logfile_with_string_embedded(dirname, "weather_station")
	print_header()
	display_adafruit.setup_for_n_m_plots(2, 2, [["temperature", "indoor", "outdoor"], ["humidity", "indoor", "outdoor"], ["pressure", "indoor"], ["particle count", "1.0", "2.5", "5.0", "10.0"]])
	display_adafruit.refresh()
	global loop_counter
	while True:
		loop()
		loop_counter += 1
	error("pct2075 is not present")
	if neopixel_is_available:
		neopixel_adafruit.set_color(0, 255, 255)

if __name__ == "__main__":
	#supervisor.disable_autoreload()
	generic.register_atexit_handler()
	try:
		main()
	except KeyboardInterrupt:
		generic.keyboard_interrupt_exception_handler()
	except ReloadException:
		generic.reload_exception_handler()
	info("leaving program...")
	flush()
	generic.reset()

