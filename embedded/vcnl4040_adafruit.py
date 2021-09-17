# https://learn.adafruit.com/adafruit-vcnl4040-proximity-sensor/python-circuitpython
# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT
# last updated 2021-09-16 by mza

import time
import board
import busio
import adafruit_vcnl4040

def setup(i2c):
	global vcnl4040
	vcnl4040 = adafruit_vcnl4040.VCNL4040(i2c)
	# https://github.com/adafruit/Adafruit_CircuitPython_VCNL4040/blob/main/adafruit_vcnl4040.py
	# https://www.vishay.com/docs/84274/vcnl4040.pdf
	#vcnl4040.light_integration_time = 0

def test_if_present():
	try:
		vcnl4040.lux
	except:
		print("vcnl4040 not present")
		return False
	return True

def measure_string():
	return ", %d, %.1f" % (vcnl4040.proximity, vcnl4040.lux)

def print_compact():
	print(measure_string())
	#print("Proximity:", vcnl4040.proximity)
	#print("Light: %d lux" % vcnl4040.lux)

if __name__ == "__main__":
	#i2c = board.I2C()
	i2c = busio.I2C(board.SCL1, board.SDA1)
	setup(i2c)
	while test_if_present():
		print_compact()
		time.sleep(1.0)

