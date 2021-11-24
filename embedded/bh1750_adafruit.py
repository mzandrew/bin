# https://learn.adafruit.com/adafruit-bh1750-ambient-light-sensor?view=all
# SPDX-FileCopyrightText: 2020 Bryan Siepert, written for Adafruit Industries
# SPDX-License-Identifier: Unlicense
# last updated 2021-11-24 by mza

import time
import board
import busio
import adafruit_bh1750
import boxcar

def setup(i2c, N):
	global bh1750
	bh1750 = adafruit_bh1750.BH1750(i2c)
	# https://github.com/adafruit/Adafruit_CircuitPython_BH1750/blob/main/adafruit_bh1750.py
	bh1750.resolution = adafruit_bh1750.Resolution.LOW
	#bh1750.mode = adafruit_bh1750.Mode.ONE_SHOT
	# https://www.mouser.com/datasheet/2/348/bh1750fvi-e-186247.pdf
	global myboxcar
	myboxcar = boxcar.boxcar(1, N, "bh1750")
	#return bh1750.i2c_device.device_address
	return 0x23
	#return 0x5c

def test_if_present():
	try:
		bh1750.lux
	except:
		print("bh1750 not present")
		return False
	return True

def get_values():
	values = [ bh1750.lux ]
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
	return ", %.1f" % values[0]

def print_compact():
	print(measure_string())

if __name__ == "__main__":
	i2c = busio.I2C(board.SCL1, board.SDA1)
	#i2c = board.I2C()
	setup(i2c)
	while test_if_present():
		print_compact()
		time.sleep(1)

