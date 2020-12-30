#!/usr/bin/env python3

# written 2020-11-25 by mza
# last updated 2020-11-25 by mza

# from https://learn.adafruit.com/adafruit-ina260-current-voltage-power-sensor-breakout/python-circuitpython
# and https://github.com/mzandrew/XRM/blob/master/predator/IV.py

import time
import sys
import board
import busio
import adafruit_ina260 # sudo pip3 install adafruit-circuitpython-ina260
from DebugInfoWarningError24 import debug, info, warning, error, debug2, debug3, set_verbosity, create_new_logfile_with_string

def setup(address=0x40):
	i2c = busio.I2C(board.SCL, board.SDA)
	global ina260
	ina260 = adafruit_ina260.INA260(i2c_bus=i2c, address=address)

header_string = ", current (mA), voltage (V), power (mW)"

def print_header():
	info("#time" + header_string)

def measure():
	I = ina260.current
	V = ina260.voltage
	P = ina260.power
	return I, V, P

def measure_string():
	I, V, P = measure()
	return "%.1f, %.3f, %.1f" % (I, V, P)

def print_compact():
	date = time.strftime("%Y-%m-%d+%X")
	string = measure_string()
	info("%s, %s" % (date, string))

def test_if_present():
	try:
		ina260.current
	except:
		return False
	return True

address = 0x40

def hex(number, width=1):
	return "%0*x" % (width, number)

if __name__ == "__main__":
	try:
		setup(address)
	except:
		error("ina260 not present at address 0x" + hex(address))
		sys.exit(1)
	create_new_logfile_with_string("ina260")
	print_header()
	while test_if_present():
		print_compact()
		sys.stdout.flush()
		time.sleep(1)

