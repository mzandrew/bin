#!/usr/bin/env python3

# written 2022-04-23 by mza
# based on temperature_log_and_graph.py
# last updated 2022-04-23 by mza

# to install on a circuitpython device:
# rsync -av *.py /media/mza/CIRCUITPY/; cp -a weather_station_portal.py /media/mza/CIRCUITPY/code.py ; sync
# ln -s ~/build/adafruit-circuitpython/bundle/lib
# cd lib
# rsync -av microcontroller adafruit_display_text adafruit_esp32spi adafruit_register adafruit_pcf8523.mpy adafruit_pct2075.mpy adafruit_displayio_sh1107.mpy neopixel.mpy adafruit_rgbled.mpy adafruit_requests.mpy adafruit_sdcard.mpy simpleio.mpy adafruit_io /media/circuitpython/lib/
# sync

import time
import sys
import atexit
import board
import busio
import displayio
#import displayio
#import digitalio
import adafruit_pct2075 # sudo pip3 install adafruit-circuitpython-pct2075
import airlift

try:
	import adafruit_dotstar as dotstar
except:
	pass
try:
	import adafruit_ht16k33.matrix
except:
	pass
try:
	import adafruit_ht16k33.segments
except:
	pass
import microsd_adafruit
import neopixel_adafruit
import pcf8523_adafruit
try:
	from DebugInfoWarningError24 import debug, info, warning, error, debug2, debug3, set_verbosity, create_new_logfile_with_string_embedded, flush
except:
	print("can't find DebugInfoWarningError24.py")
	sys.exit(0)
import generic
import display_adafruit

import adafruit_pyportal
import adafruit_touchscreen
import adafruit_hx8357
#width = 480
#height = 320

intensity = 8 # brightness of plotted data on dotstar display
if 1:
	feed = "scoopy-boops"
	offset_t = 25.0 # min temp we care to plot
	max_t = 75.0 # max temp we care to plot
	N = 5*60 # number of samples to average over
	delay = 1.0 # number of seconds between samples
	#should_use_airlift = True
	should_use_airlift = False
	should_use_dotstar_matrix = False
	should_use_matrix_backpack = False
	should_use_alphanumeric_backpack = False
	should_use_sh1107_oled_display = False
	should_use_ssd1327_oled_display = False
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
temperatures_to_plot = [ -40.0 for a in range(MAX_COLUMNS_TO_PLOT) ]

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

def setup_dotstar_matrix(auto_write = True):
	if not should_use_dotstar_matrix:
		return False
	global dots
	#dots.deinit()
	try:
		dots = dotstar.DotStar(board.D13, board.D11, 72, brightness=0.1)
		dots.auto_write = False
		dots.show()
		dots.auto_write = auto_write
	except:
		error("error setting up dotstar matrix")
		return False
	return True

def update_temperature_display_on_dotstar_matrix():
	if not dotstar_matrix_is_available:
		return
	dots.auto_write = False
	rows = 6
	columns = 12
	gain_t = (max_t - offset_t) / (rows - 1)
	for y in range(rows):
		for x in range(columns):
			index = y * columns + x
			dots[index] = (0, 0, 0)
	for x in range(columns):
		if 0.0<temperatures_to_plot[x]:
			y = (temperatures_to_plot[x] - offset_t) / gain_t
			if y<0.0:
				y = 0
			if rows<=y:
				y = rows - 1
			index = int(y) * columns + columns - 1 - x
			red = intensity * y
			green = 0
			blue = intensity * (rows-1) - red
			dots[index] = (red, green, blue)
	dots.show()

def setup_matrix_backpack():
	if not should_use_matrix_backpack:
		return False
	global matrix_backpack
	try:
		matrix_backpack = adafruit_ht16k33.matrix.Matrix16x8(i2c, address=0x70)
		#matrix_backpack.fill(1)
		matrix_backpack.auto_write = False
		#matrix_backpack.brightness = 0.5
		#matrix_backpack.blink_rate = 0
	except:
		return False
	return True

def setup_alphanumeric_backpack(address=0x70):
	if not should_use_alphanumeric_backpack:
		return False
	global alphanumeric_backpack
	try:
		alphanumeric_backpack = adafruit_ht16k33.segments.Seg14x4(i2c, address=address)
		alphanumeric_backpack.auto_write = False
		#alphanumeric_backpack.brightness = 0.5
		#alphanumeric_backpack.blink_rate = 0
	except:
		error("can't find alphanumeric backpack (i2c address " + hex(address) + ")")
		return False
	return True

def update_temperature_display_on_matrix_backpack():
	if not matrix_backpack_available:
		return
	matrix_backpack.auto_write = False
	rows = 8
	columns = 16
	gain_t = (max_t - offset_t) / (rows - 1)
	matrix_backpack.fill(0)
	for x in range(columns):
		if 0.0<temperatures_to_plot[x]:
			y = (temperatures_to_plot[x] - offset_t) / gain_t
			if y<0.0:
				y = 0
			if rows<=y:
				y = rows - 1
			y = int(y)
			matrix_backpack[columns - 1 - x, y] = 1
			#info("matrix_backpack[" + str(x) + ", " + str(y) + "]")
	matrix_backpack.show()

def update_temperature_display_on_alphanumeric_backpack(temperature):
	if not alphanumeric_backpack_available:
		return
	alphanumeric_backpack.auto_write = False
	alphanumeric_backpack.fill(0)
	value = int(10.0*temperature)/10.0
	#info(str(value))
	alphanumeric_backpack.print(str(value))
	#alphanumeric_backpack[0] = '0'
	#alphanumeric_backpack[1] = '1'
	#alphanumeric_backpack[2] = '2'
	#alphanumeric_backpack[3] = '3'
	#DIGIT_2 = 0b000011111011
	#alphanumeric_backpack.set_digit_raw(0, DIGIT_2)
	alphanumeric_backpack.show()

def loop():
#	temperature_accumulator = 0.0
#	for i in range(N):
#		if neopixel_is_available:
#			neopixel_adafruit.set_color(255, 0, 0)
#		print_compact()
#		temperature_accumulator += temperature
#		if neopixel_is_available:
#			neopixel_adafruit.set_color(0, 255, 0)
#		flush()
#		time.sleep(delay)
#		update_temperature_display_on_alphanumeric_backpack(temperature)
#	average_temperature = temperature_accumulator/N
#	print("posting " + str(average_temperature))
#	airlift.post_data("water-heater", average_temperature)
#	temperatures_to_plot.insert(0, average_temperature)
#	temperatures_to_plot.pop()
#	update_temperature_display_on_dotstar_matrix()
#	update_temperature_display_on_matrix_backpack()
#	if should_use_ssd1327_oled_display:
#		if oled_display_is_available and should_plot_temperatures:
#			display_adafruit.update_temperature_display_on_oled_ssd1327(temperatures_to_plot)
#	if should_use_sh1107_oled_display:
#		if oled_display_is_available and should_plot_temperatures:
#			display_adafruit.update_temperature_display_on_oled_sh1107(offset_t, max_t, temperatures_to_plot)
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
		myarray_c = [ 0.19 + 0.3*i/display_adafruit.plot_height for i in range(display_adafruit.plot_width) ]
		myarray_d = [ 0.12 + 0.2*i/display_adafruit.plot_width for i in range(display_adafruit.plot_width) ]
		display_adafruit.update_plot(1, [myarray_a, myarray_b, myarray_c, myarray_d])
	elif 2==lcm4:
		myarray_a = [ 0.1 + 0.5*i/display_adafruit.plot_height for i in range(display_adafruit.plot_width) ]
		myarray_b = [ 0.15 + 0.4*i/display_adafruit.plot_width for i in range(display_adafruit.plot_width) ]
		display_adafruit.update_plot(2, [myarray_a, myarray_b])
	else:
		myarray_c = [ 0.55 - 0.1 * i/display_adafruit.plot_height for i in range(display_adafruit.plot_width) ]
		display_adafruit.update_plot(3, [myarray_c])
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
	global dotstar_matrix_is_available
	dotstar_matrix_is_available = setup_dotstar_matrix(False)
	global i2c
	try:
		i2c = busio.I2C(board.SCL1, board.SDA1)
		info("using I2C1")
	except:
		i2c = busio.I2C(board.SCL, board.SDA)
		info("using I2C0")
	try:
		setup_temperature_sensors(i2c)
	except:
		error("can't find any temperature sensors on i2c bus")
	global oled_display_is_available
	if should_use_ssd1327_oled_display:
		oled_display_is_available = display_adafruit.setup_i2c_oled_display_ssd1327(i2c, 0x3d)
		if oled_display_is_available:
			display_adafruit.clear_display_on_oled_ssd1327()
	if should_use_sh1107_oled_display:
		oled_display_is_available = display_adafruit.setup_i2c_oled_display_sh1107(i2c, 0x3c)
		if oled_display_is_available:
			display_adafruit.clear_display_on_oled_sh1107()
	global display_is_available
	if should_use_hx8357_lcd:
		display_is_available = display_adafruit.setup_builtin_lcd_hx8357()
	global matrix_backpack_available
	try:
		matrix_backpack_available = setup_matrix_backpack()
	except:
		error("can't find matrix backpack (i2c address 0x70)")
		matrix_backpack_available = False
	global alphanumeric_backpack_available
	alphanumeric_backpack_available = setup_alphanumeric_backpack(0x77)
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
	display_adafruit.setup_for_four_plots()
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

