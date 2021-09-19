# https://learn.adafruit.com/adafruit-bh1750-ambient-light-sensor?view=all
# SPDX-FileCopyrightText: 2020 Bryan Siepert, written for Adafruit Industries
# last updated 2021-09-19 by mza

# SPDX-License-Identifier: Unlicense
import time
import board
import busio
import adafruit_bh1750

def setup(i2c):
	global bh1750
	bh1750 = adafruit_bh1750.BH1750(i2c)
	# https://github.com/adafruit/Adafruit_CircuitPython_BH1750/blob/main/adafruit_bh1750.py
	bh1750.resolution = adafruit_bh1750.Resolution.LOW
	#bh1750.mode = adafruit_bh1750.Mode.ONE_SHOT
	# https://www.mouser.com/datasheet/2/348/bh1750fvi-e-186247.pdf
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

def measure_string():
	return ", %.2f" % bh1750.lux

def print_compact():
	print(measure_string())

if __name__ == "__main__":
	i2c = busio.I2C(board.SCL1, board.SDA1)
	#i2c = board.I2C()
	setup(i2c)
	while test_if_present():
		print_compact()
		time.sleep(1)

