#!/usr/bin/env python3

# written 2020-11-24 by mza
# last updated 2020-11-25 by mza

# from https://learn.adafruit.com/adafruit-pct2075-temperature-sensor/python-circuitpython

import time
import sys
import board
import busio
import adafruit_pct2075

def setup():
	i2c = busio.I2C(board.SCL, board.SDA)
	global pct
	pct = adafruit_pct2075.PCT2075(i2c)

header_string = ", temperature (C)"

def print_header():
	print("#time" + header_string)

def measure():
	return pct.temperature

def measure_string():
	temp = measure()
	return "%.1f" % temp

def print_compact():
	date = time.strftime("%Y-%m-%d+%X")
	string = measure_string()
	print("%s, %s" % (date, string))

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
		print("pct2075 not present")
		sys.exit(1)
	print_header()
	while test_if_present():
		print_compact()
		sys.stdout.flush()
		time.sleep(1)

