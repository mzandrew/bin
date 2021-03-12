#!/usr/bin/env python3

# written 2020-11-24 by mza
# last updated 2020-12-18 by mza

# from https://learn.adafruit.com/adafruit-pct2075-temperature-sensor/python-circuitpython

import time
import sys
import board
import busio
import adafruit_pct2075 # sudo pip3 install adafruit-circuitpython-pct2075/
from DebugInfoWarningError24 import debug, info, warning, error, debug2, debug3, set_verbosity, create_new_logfile_with_string

def setup():
	i2c = busio.I2C(board.SCL, board.SDA)
	global pct
	pct = adafruit_pct2075.PCT2075(i2c)

header_string = ", temperature (C)"

def print_header():
	info("#time" + header_string)

def measure():
	return pct.temperature

def measure_string():
	temp = measure()
	return "%.1f" % temp

def print_compact():
	date = time.strftime("%Y-%m-%d+%X")
	string = measure_string()
	info("%s, %s" % (date, string))

def test_if_present():
	try:
		pct.temperature
	except:
		return False
	return True

if __name__ == "__main__":
	try:
		setup()
	except:
		error("pct2075 not present")
		sys.exit(1)
	create_new_logfile_with_string("pct2075")
	print_header()
	while test_if_present():
		print_compact()
		sys.stdout.flush()
		time.sleep(1)

