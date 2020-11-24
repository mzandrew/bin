#!/usr/bin/env python3

# written 2020-11-24 by mza

# from https://learn.adafruit.com/adafruit-pct2075-temperature-sensor/python-circuitpython

import time
import sys
import board
import busio
import adafruit_pct2075

i2c = busio.I2C(board.SCL, board.SDA)
pct = adafruit_pct2075.PCT2075(i2c)

#def once():
#	temp = pct.temperature
#	string = "%.1f C" % temp
#	print(string)
#once

def print_header():
	print("#time, temperature (C)")

def print_compact():
	print("%s, %0.1f" % (time.strftime("%Y-%m-%d+%X"),pct.temperature))

print_header()
while True:
	#print_verbose()
	print_compact()
	sys.stdout.flush()
	time.sleep(1)

