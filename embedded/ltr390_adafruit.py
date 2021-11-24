# https://learn.adafruit.com/adafruit-ltr390-uv-sensor/python-circuitpython
# https://github.com/adafruit/Adafruit_CircuitPython_LTR390
# SPDX-FileCopyrightText: 2021 by Bryan Siepert, written for Adafruit Industries
# SPDX-License-Identifier: Unlicense
# last updated 2021-11-24 by mza

import time
import board
import busio
import adafruit_ltr390
import boxcar

def setup(i2c, N):
	global ltr390
	ltr390 = adafruit_ltr390.LTR390(i2c)
	# https://github.com/adafruit/Adafruit_CircuitPython_LTR390/blob/main/adafruit_ltr390.py
	# adafruit values are gain=1 resolution=4 and _rate_bits=4
	# mfg reset values are gain=1 resolution=2 and _rate_bits=2
	# https://optoelectronics.liteon.com/upload/download/DS86-2015-0004/LTR-390UV_Final_%20DS_V1%201.pdf
	ltr390.gain = 0
	# gain=0 means gain is 1
	# gain=1 means gain is 3 (default)
	# gain=2 means gain is 6
	# gain=3 means gain is 9
	# gain=4 means gain is 18
	#ltr390.resolution = 2
	ltr390._rate_bits = 2
	#lux_calc = wfac * 0.6 * als_data / (gain*integration_time)
	global myboxcar
	myboxcar = boxcar.boxcar(4, N, "ltr390")
	#return ltr390.i2c_device.device_address
	return 0x53

def test_if_present():
	try:
		#ltr390.lux
		ltr390.light
	except:
		print("ltr390 not present")
		return False
	return True

def get_values():
	values = [ ltr390.uvs, ltr390.uvi, ltr390.light, ltr390.lux ]
	myboxcar.accumulate(values)
	return values

def show_average_values():
	myboxcar.show_average_values()

def get_average_values():
	return myboxcar.get_average_values()

def get_previous_values():
	return myboxcar.previous_values()

def measure_string():
	values = get_values()
	return ", %d, %d, %d, %d" % (values[0], values[1], values[2], values[3])

def print_compact():
	print(measure_string())
	#print("UV:", ltr390.uvs, "\t\tAmbient Light:", ltr390.light)
	#print("UVI:", ltr390.uvi, "\t\tLux:", ltr390.lux)

if __name__ == "__main__":
	i2c = busio.I2C(board.SCL1, board.SDA1)
	#i2c = board.I2C()
	setup(i2c)
	while test_if_present():
		print_compact()
		time.sleep(1)

