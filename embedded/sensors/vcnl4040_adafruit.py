# https://learn.adafruit.com/adafruit-vcnl4040-proximity-sensor/python-circuitpython
# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT
# last updated 2021-11-24 by mza

import time
import board
import busio
import adafruit_vcnl4040
import boxcar

def setup(i2c, N):
	global vcnl4040
	vcnl4040 = adafruit_vcnl4040.VCNL4040(i2c)
	# https://github.com/adafruit/Adafruit_CircuitPython_VCNL4040/blob/main/adafruit_vcnl4040.py
	# https://www.vishay.com/docs/84274/vcnl4040.pdf
	#vcnl4040.light_integration_time = 0
	global myboxcar
	myboxcar = boxcar.boxcar(2, N, "vcnl4040")
	#return vcnl4040.i2c_device.device_address
	return 0x60

def test_if_present():
	try:
		vcnl4040.lux
	except:
		print("vcnl4040 not present")
		return False
	return True

def get_values():
	values = [ vcnl4040.proximity, vcnl4040.lux ]
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
	return ", %d, %.1f" % (values[0], values[1])

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

