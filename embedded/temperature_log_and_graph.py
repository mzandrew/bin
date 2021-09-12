#!/usr/bin/env python3

# written 2021-04-21 by mza
# last updated 2021-09-12 by mza

# to install on a circuitpython device:
# cp DebugInfoWarningError24.py pcf8523_adafruit.py /media/circuitpython/
# cp temperature_log_and_graph.py /media/circuitpython/code.py
# cd ~/build/adafruit-circuitpython/bundle/lib
# rsync -r adafruit_esp32spi adafruit_register adafruit_pcf8523.mpy adafruit_pct2075.mpy adafruit_displayio_sh1107.mpy neopixel.mpy adafruit_rgbled.mpy adafruit_requests.mpy adafruit_sdcard.mpy simpleio.mpy /media/circuitpython/lib/

import time
import sys
import board
import busio
import displayio
import digitalio
import neopixel
import adafruit_pct2075 # sudo pip3 install adafruit-circuitpython-pct2075
import adafruit_register
import microsd_adafruit
import storage
import adafruit_bus_device
from adafruit_esp32spi import adafruit_esp32spi
from adafruit_esp32spi import adafruit_esp32spi_wifimanager
from adafruit_esp32spi import PWMOut
import adafruit_requests as requests
import adafruit_esp32spi.adafruit_esp32spi_socket as socket
import adafruit_displayio_sh1107
from DebugInfoWarningError24 import debug, info, warning, error, debug2, debug3, set_verbosity, create_new_logfile_with_string_embedded, flush
import pcf8523_adafruit
try:
	import adafruit_ssd1327 # sudo pip3 install adafruit-circuitpython-ssd1327
except:
	pass
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

intensity = 8 # brightness of plotted data on dotstar display
if 1:
	feed = "heater"
	offset_t = 45.0 # min temp we care to plot
	max_t = 65.0 # max temp we care to plot
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
else:
	feed = "test"
	offset_t = 25.4 # min temp we care to plot
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

temperature_sensors = []
header_string = "heater"
temperature = 0
dir = "/logs"

max_columns_to_plot = 128
temperatures_to_plot = [ -40.0 for a in range(max_columns_to_plot) ]

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

def setup_i2c_oled_display_ssd1327(address):
	if not should_use_ssd1327_oled_display:
		return False
	global display
	try:
		display_bus = displayio.I2CDisplay(i2c, device_address=address)
		display = adafruit_ssd1327.SSD1327(display_bus, width=128, height=128)
	except:
		error("can't initialize ssd1327 display over i2c (address " + hex(address) + ")")
		return False
	return True

def setup_i2c_oled_display_sh1107(address):
	if not should_use_sh1107_oled_display:
		return False
	#oled_reset = board.D9
	global display
	try:
		display_bus = displayio.I2CDisplay(i2c, device_address=address)
		display = adafruit_displayio_sh1107.SH1107(display_bus, width=128, height=64)
		display.auto_refresh = False
	except:
		error("can't initialize sh1107 display over i2c (address " + hex(address) + ")")
		return False
	return True

def clear_display_on_oled_ssd1327():
	if not oled_display_is_available:
		return
	global bitmap
	bitmap = displayio.Bitmap(128, 128, 2)
	palette = displayio.Palette(2)
	palette[0] = 0x000000
	palette[1] = 0xffffff
	tile_grid = displayio.TileGrid(bitmap, pixel_shader = palette)
	group = displayio.Group()
	group.append(tile_grid)
	for x in range(128):
		for y in range(128):
			bitmap[x,y] = 0
	display.show(group)
	display.refresh()

def clear_display_on_oled_sh1107():
	if not oled_display_is_available:
		return
	global bitmap
	bitmap = displayio.Bitmap(128, 64, 2)
	palette = displayio.Palette(2)
	palette[0] = 0x000000
	palette[1] = 0xffffff
	tile_grid = displayio.TileGrid(bitmap, pixel_shader = palette)
	group = displayio.Group()
	group.append(tile_grid)
	for x in range(128):
		for y in range(64):
			bitmap[x,y] = 0
	display.show(group)
	display.refresh()

def update_temperature_display_on_oled_ssd1327():
	if not oled_display_is_available:
		return
	global bitmap
	display.auto_refresh = False
	rows = 128
	columns = 128
	gain_t = (max_t - offset_t) / (rows - 1)
	for y in range(rows):
		for x in range(columns):
			bitmap[x, y] = 0
	for x in range(columns):
		if 0.0<temperatures_to_plot[x]:
			y = rows - 1 - int((temperatures_to_plot[x] - offset_t) / gain_t)
			if y<0.0:
				y = 0
			if rows<=y:
				y = rows - 1
			bitmap[columns - 1 - x, y] = 1
	display.refresh()

def update_temperature_display_on_oled_sh1107():
	if not oled_display_is_available:
		return
	global bitmap
	display.auto_refresh = False
	rows = 64
	columns = 128
	gain_t = (max_t - offset_t) / (rows - 1)
	for y in range(rows):
		for x in range(columns):
			bitmap[x, y] = 0
	for x in range(columns):
		if 0.0<temperatures_to_plot[x]:
			y = rows - 1 - int((temperatures_to_plot[x] - offset_t) / gain_t)
			if y<0.0:
				y = 0
			if rows<=y:
				y = rows - 1
			bitmap[columns - 1 - x, y] = 1
	display.refresh()

def setup_neopixel():
	global pixel
	try:
		pixel = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0.01, auto_write=True)
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

def setup_airlift():
	global wifi
	global secrets
	if not should_use_airlift:
		return False
	# from https://github.com/ladyada/Adafruit_CircuitPython_ESP32SPI/blob/master/examples/esp32spi_localtime.py
	# and https://learn.adafruit.com/adafruit-airlift-featherwing-esp32-wifi-co-processor-featherwing?view=all
	try:
		from secrets import secrets
	except ImportError:
		print("WiFi secrets are kept in secrets.py, please add them there!")
		return False
	try:
		esp32_cs = digitalio.DigitalInOut(board.D13)
		esp32_ready = digitalio.DigitalInOut(board.D11)
		esp32_reset = digitalio.DigitalInOut(board.D12)
		spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
		esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)
		print("Connecting to " + secrets["ssid"] + " ...")
		while not esp.is_connected:
			try:
				esp.connect_AP(secrets["ssid"], secrets["password"])
			except RuntimeError as e:
				print("could not connect to AP, retrying: ", e)
				continue
		print("My IP address is", esp.pretty_ip(esp.ip_address))
		try:
			import adafruit_rgbled
		except:
			error("you need adafruit_rgbled.mpy and/or simpleio.mpy")
			raise
		RED_LED = PWMOut.PWMOut(esp, 26)
		GREEN_LED = PWMOut.PWMOut(esp, 25)
		BLUE_LED = PWMOut.PWMOut(esp, 27)
		status_light = adafruit_rgbled.RGBLED(RED_LED, BLUE_LED, GREEN_LED)
		wifi = adafruit_esp32spi_wifimanager.ESPSPI_WiFiManager(esp, secrets, status_light)
	except:
		error("can't initialize airlift wifi")
		return False
	return True

def post_data(data):
	if not airlift_is_available:
		return
	try:
		payload = {"value": data}
		url = "https://io.adafruit.com/api/v2/" + secrets["aio_username"] + "/feeds/" + feed + "/data"
		response = wifi.post(url, json=payload, headers={"X-AIO-KEY": secrets["aio_key"]})
		#print(response.json())
		response.close()
	except:
		error("couldn't perform POST operation")

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

if __name__ == "__main__":
	try:
		displayio.release_displays()
	except:
		pass
	try:
		neopixel_is_available = setup_neopixel()
	except:
		error("error setting up neopixel")
		neopixel_is_available = False
	dotstar_matrix_is_available = setup_dotstar_matrix(False)
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
	if should_use_ssd1327_oled_display:
		oled_display_is_available = setup_i2c_oled_display_ssd1327(0x3d)
		clear_display_on_oled_ssd1327()
	if should_use_sh1107_oled_display:
		oled_display_is_available = setup_i2c_oled_display_sh1107(0x3c)
		clear_display_on_oled_sh1107()
	airlift_is_available = setup_airlift()
	try:
		matrix_backpack_available = setup_matrix_backpack()
	except:
		error("can't find matrix backpack (i2c address 0x70)")
		matrix_backpack_available = False
	alphanumeric_backpack_available = setup_alphanumeric_backpack(0x77)
	if should_use_RTC:
		RTC_is_available = pcf8523_adafruit.setup(i2c)
	else:
		RTC_is_available = False
	if should_use_sdcard:
		sdcard_is_available = setup_sdcard_for_logging_data(dir)
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
		temperature_accumulator = 0.0
		for i in range(N):
			if neopixel_is_available:
				try:
					pixel.fill((255, 0, 0))
				except:
					pass
			print_compact()
			temperature_accumulator += temperature
			if neopixel_is_available:
				try:
					pixel.fill((0, 255, 0))
				except:
					pass
			try:
				sys.stdout.flush()
			except:
				pass
			time.sleep(delay)
			update_temperature_display_on_alphanumeric_backpack(temperature)
		average_temperature = temperature_accumulator/N
		post_data(average_temperature)
		temperatures_to_plot.insert(0, average_temperature)
		temperatures_to_plot.pop()
		update_temperature_display_on_dotstar_matrix()
		update_temperature_display_on_matrix_backpack()
		if should_use_ssd1327_oled_display:
			update_temperature_display_on_oled_ssd1327()
		if should_use_sh1107_oled_display:
			update_temperature_display_on_oled_sh1107()
		flush()

