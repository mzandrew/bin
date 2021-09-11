# https://learn.adafruit.com/adafruit-ltr390-uv-sensor/python-circuitpython
# https://github.com/adafruit/Adafruit_CircuitPython_LTR390
# SPDX-FileCopyrightText: 2021 by Bryan Siepert, written for Adafruit Industries
# SPDX-License-Identifier: Unlicense
# last updated 2021-09-10 by mza

import time
import board
import busio
import adafruit_ltr390

def setup(i2c):
	global ltr390
	ltr390 = adafruit_ltr390.LTR390(i2c)

def test_if_present():
	try:
		#ltr390.lux
		ltr390.light
	except:
		print("ltr390 not present")
		return False
	return True

def measure_string():
	return ", %d, %d" % (ltr390.uvs, ltr390.light)

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

