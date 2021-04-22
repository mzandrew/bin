#!/usr/bin/env python3

# written 2021-04-21 by mza
# last updated 2021-04-2by mza

import time
import sys
import board
import busio
import displayio
import adafruit_pct2075 # sudo pip3 install adafruit-circuitpython-pct2075
import adafruit_ssd1327 # sudo pip3 install adafruit-circuitpython-ssd1327
from DebugInfoWarningError24 import debug, info, warning, error, debug2, debug3, set_verbosity, create_new_logfile_with_string

def setup_temperature_sensor(address):
	#i2c.deinit()
	global pct
	pct = adafruit_pct2075.PCT2075(i2c, address=address)

displayio.release_displays()
header_string = "temperature (C)"

def print_header():
	info("#" + header_string)

def measure():
	return pct.temperature

def measure_string():
	temp = measure()
	return "%.1f" % temp

def print_compact():
	try:
		date = time.strftime("%Y-%m-%d+%X, ")
	except:
		date = ""
	string = measure_string()
	info("%s%s" % (date, string))

def test_if_present():
	try:
		pct.temperature
	except:
		return False
	return True

def setup_i2c_oled_display(address):
	display_bus = displayio.I2CDisplay(i2c, device_address=address)
	global display
	display = adafruit_ssd1327.SSD1327(display_bus, width=128, height=128)

if __name__ == "__main__":
	#info("start")
	i2c = busio.I2C(board.SCL1, board.SDA1)
	#info("temperature sensor")
	try:
		setup_temperature_sensor(0x37)
	except:
		error("pct2075 not present (address 0x37)")
		sys.exit(1)
	#info("display")
	try:
		setup_i2c_oled_display(0x3d)
	except:
		error("can't initialize ssd1327 display over i2c (address 0x3d)")
		sys.exit(1)
	#info("continue")
	create_new_logfile_with_string("pct2075")
	print_header()
	while test_if_present():
		print_compact()
		try:
			sys.stdout.flush()
		except:
			pass
		time.sleep(1)

