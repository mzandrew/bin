#!/usr/bin/env python3

# written 2021-04-21 by mza
# last updated 2021-12-29 by mza

# to install on a circuitpython device:
# rsync -r *.py /media/circuitpython/
# cp -a temperature_log_and_graph.py /media/circuitpython/code.py
# ln -s ~/build/adafruit-circuitpython/bundle/lib
# cd lib
# rsync -av microcontroller adafruit_display_text adafruit_esp32spi adafruit_register adafruit_pcf8523.mpy adafruit_pct2075.mpy adafruit_displayio_sh1107.mpy neopixel.mpy adafruit_rgbled.mpy adafruit_requests.mpy adafruit_sdcard.mpy simpleio.mpy adafruit_io /media/circuitpython/lib/
# sync

import time
import sys
import atexit
import supervisor
import board
import busio
import displayio
import digitalio
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
import oled_adafruit
from DebugInfoWarningError24 import debug, info, warning, error, debug2, debug3, set_verbosity, create_new_logfile_with_string_embedded, flush
import generic

intensity = 8 # brightness of plotted data on dotstar display
if 1:
	feed = "heater"
	offset_t = 25.0 # min temp we care to plot
	max_t = 75.0 # max temp we care to plot
	N = 5*60 # number of samples to average over
	delay = 1.0 # number of seconds between samples
	should_use_airlift = True
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
	should_use_airlift = True
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
dir = "/logs"

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
	temperature_accumulator = 0.0
	for i in range(N):
		if neopixel_is_available:
			neopixel_adafruit.set_color(255, 0, 0)
		print_compact()
		temperature_accumulator += temperature
		if neopixel_is_available:
			neopixel_adafruit.set_color(0, 255, 0)
		flush()
		time.sleep(delay)
		update_temperature_display_on_alphanumeric_backpack(temperature)
	average_temperature = temperature_accumulator/N
	print("posting " + str(average_temperature))
	airlift.post_data("heater", average_temperature)
	temperatures_to_plot.insert(0, average_temperature)
	temperatures_to_plot.pop()
	update_temperature_display_on_dotstar_matrix()
	update_temperature_display_on_matrix_backpack()
	if should_use_ssd1327_oled_display:
		if oled_display_is_available and should_plot_temperatures:
			oled_adafruit.update_temperature_display_on_oled_ssd1327(temperatures_to_plot)
	if should_use_sh1107_oled_display:
		if oled_display_is_available and should_plot_temperatures:
			oled_adafruit.update_temperature_display_on_oled_sh1107(offset_t, max_t, temperatures_to_plot)
	flush()

def main():
	try:
		displayio.release_displays()
	except:
		pass
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
		oled_display_is_available = oled_adafruit.setup_i2c_oled_display_ssd1327(i2c, 0x3d)
		if oled_display_is_available:
			oled_adafruit.clear_display_on_oled_ssd1327()
	if should_use_sh1107_oled_display:
		oled_display_is_available = oled_adafruit.setup_i2c_oled_display_sh1107(i2c, 0x3c)
		if oled_display_is_available:
			oled_adafruit.clear_display_on_oled_sh1107()
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
		airlift_is_available = airlift.setup_airlift("water-heater", spi, board.D13, board.D11, board.D12)
	else:
		airlift_is_available = False
	if airlift_is_available:
		airlift.setup_feed(feed)
	if 0:
		print("fetching old data from feed...")
		global temperatures_to_plot
		temperatures_to_plot = airlift.get_all_data(MAX_COLUMNS_TO_PLOT)
	global sdcard_is_available
	if should_use_sdcard:
		sdcard_is_available = setup_sdcard_for_logging_data(spi, dir)
	else:
		sdcard_is_available = False
	if not sdcard_is_available:
		dir = "/"
	if RTC_is_available:
		create_new_logfile_with_string_embedded(dir, "pct2075", pcf8523_adafruit.get_timestring2())
	else:
		create_new_logfile_with_string_embedded(dir, "pct2075")
	print_header()
	while test_if_present():
		loop()
	error("pct2075 is not present")
	if neopixel_is_available:
		neopixel_adafruit.set_color(0, 255, 255)

if __name__ == "__main__":
	#supervisor.disable_autoreload()
	atexit.register(generic.reset)
	try:
		main()
	except KeyboardInterrupt:
		info("caught ctrl-c")
		flush()
		atexit.unregister(generic.reset)
		sys.exit(0)
	except ReloadException:
		info("reload exception")
		flush()
		atexit.unregister(generic.reset)
		time.sleep(1)
		supervisor.reload()
	info("leaving program...")
	flush()
	generic.reset()

