#!/usr/bin/env python3

# written 2021-04-21 by mza
# last updated 2021-05-01 by mza

import time
import sys
import board
import busio
import displayio
import digitalio
import neopixel
import adafruit_pct2075 # sudo pip3 install adafruit-circuitpython-pct2075
import adafruit_ssd1327 # sudo pip3 install adafruit-circuitpython-ssd1327
import adafruit_dotstar as dotstar
from DebugInfoWarningError24 import debug, info, warning, error, debug2, debug3, set_verbosity, create_new_logfile_with_string_embedded

intensity = 8 # brightness of plotted data on dotstar display
if 0:
	offset_t = 45.0 # min temp we care to plot
	max_t = 65.0 # max temp we care to plot
	N = 5*60 # number of seconds to average over
	feed = "heater"
else:
	offset_t = 26.0 # min temp we care to plot
	max_t = 28.0 # max temp we care to plot
	N = 1*60 # number of seconds to average over
	feed = "test"
should_use_airlift = True
should_use_dotstar_matrix = False

temperature_sensors = []
header_string = "heater"
temperature = 0

def setup_temperature_sensor(address):
	#i2c.deinit()
	global temperature_sensors
	temperature_sensors.append(adafruit_pct2075.PCT2075(i2c, address=address))
	return 1

def setup_temperature_sensors():
	global header_string
	count = 0
	for address in [0x37, 0x36, 0x35, 0x2, 0x2e, 0x2d, 0x2c, 0x2b, 0x2a, 0x29, 0x28, 0x77, 0x76, 0x75, 0x74, 0x73, 0x72, 0x71, 0x70, 0x4f, 0x4e, 0x4d, 0x4c, 0x4b, 0x4a, 0x49, 0x48]:
		try:
			count += setup_temperature_sensor(address)
			if 1!=count:
				header_string += ", other" + str(count)
		except:
			pass
	if 0==count:
		error("pct2075 not present (any i2c address)")
	else:
		info("found " + str(count) + " temperature sensors")
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
		date = ""
	string = measure_string()
	info("%s%s" % (date, string))

def test_if_present():
	try:
		temperature_sensors[0].temperature
	except:
		return False
	return True

def setup_i2c_oled_display(address):
	global display
	try:
		display_bus = displayio.I2CDisplay(i2c, device_address=address)
		display = adafruit_ssd1327.SSD1327(display_bus, width=128, height=128)
	except:
		return False
	return True

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
			if y<0:
				y = 0
			if rows<y:
				y = rows - 1
			index = int(y) * columns + x
			red = intensity * y
			green = 0
			blue = intensity * (rows-1) - red
			dots[index] = (red, green, blue)
	dots.show()

temperatures_to_plot = [ -40.0 for a in range(12) ]

from adafruit_esp32spi import adafruit_esp32spi
from adafruit_esp32spi import adafruit_esp32spi_wifimanager
import adafruit_requests as requests
import adafruit_esp32spi.adafruit_esp32spi_socket as socket

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
		import adafruit_rgbled
		from adafruit_esp32spi import PWMOut
		RED_LED = PWMOut.PWMOut(esp, 26)
		GREEN_LED = PWMOut.PWMOut(esp, 25)
		BLUE_LED = PWMOut.PWMOut(esp, 27)
		status_light = adafruit_rgbled.RGBLED(RED_LED, BLUE_LED, GREEN_LED)
		wifi = adafruit_esp32spi_wifimanager.ESPSPI_WiFiManager(esp, secrets, status_light)
	except:
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
	try:
		dotstar_matrix_is_available = setup_dotstar_matrix(False)
	except:
		error("error setting up dotstar matrix")
		dotstar_matrix_is_available = False
	try:
		i2c = busio.I2C(board.SCL1, board.SDA1)
	except:
		i2c = busio.I2C(board.SCL, board.SDA)
	try:
		setup_temperature_sensors()
	except:
		error("can't find any temperature sensors on i2c bus")
	try:
		oled_display_is_available = setup_i2c_oled_display(0x3d)
	except:
		error("can't initialize ssd1327 display over i2c (address 0x3d)")
		oled_display_is_available = False
	try:
		airlift_is_available = setup_airlift()
	except:
		error("can't initialize airlift wifi")
		airlift_is_available = False
	create_new_logfile_with_string_embedded("pct2075")
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
			#time.sleep(54/60)
			time.sleep(1)
		average_temperature = temperature_accumulator/N
		post_data(average_temperature)
		temperatures_to_plot.append(average_temperature)
		temperatures_to_plot.pop(0)
		update_temperature_display_on_dotstar_matrix()
