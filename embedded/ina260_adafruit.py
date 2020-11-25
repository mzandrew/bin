#!/usr/bin/env python3

# written 2020-11-25 by mza

# from https://learn.adafruit.com/adafruit-ina260-current-voltage-power-sensor-breakout/python-circuitpython
# and https://github.com/mzandrew/XRM/blob/master/predator/IV.py

import time
import sys
import board
import busio
import adafruit_ina260 # sudo pip3 install adafruit-circuitpython-ina260

i2c = busio.I2C(board.SCL, board.SDA)
ina260 = adafruit_ina260.INA260(i2c_bus=i2c, address=0x40)

def print_header():
	print("#time, current (mA), voltage (V), power (mW)")

def print_compact():
	date = time.strftime("%Y-%m-%d+%X")
	I = ina260.current
	V = ina260.voltage
	P = ina260.power
	print("%s, %.1f, %.3f, %.1f" % (date, I, V, P))

print_header()
while True:
	#print_verbose()
	print_compact()
	sys.stdout.flush()
	time.sleep(1)

