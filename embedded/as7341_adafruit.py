# https://learn.adafruit.com/adafruit-as7341-10-channel-light-color-sensor-breakout/python-circuitpython
# SPDX-FileCopyrightText: 2020 Bryan Siepert, written for Adafruit Industries
# SPDX-License-Identifier: MIT
# last updated 2022-07-09 by mza

import time
import board
import adafruit_as7341
import boxcar

def setup(i2c, N):
	global as7341
	as7341 = adafruit_as7341.AS7341(i2c)
	# https://github.com/adafruit/Adafruit_CircuitPython_AS7341/blob/main/adafruit_as7341.py
	# adafruit default is atime=100 and astep=999
	# mfg recommendation is atime=29 and astep=599
	# https://ams.com/documents/20143/36005/AS7341_DS000504_3-00.pdf
	as7341.atime = 29 # number of ATIME durations to accumulate light (0-255)
	as7341.astep = 599 # integration time per ASTEP (2.78us each) (0-65534)
	# adc_fullscale = (atime+1)*(astep+1)
	as7341.gain = 0
	global myboxcar
	myboxcar = boxcar.boxcar(10, N, "as7341")
	#return as7341.i2c_device.device_address
	return 0x39

def test_if_present():
	try:
		as7341.channel_415nm
	except:
		return False
	return True

def bar_graph(read_value):
	scaled = int(read_value / 1000)
	return "[%5d] " % read_value + (scaled * "*")

def get_values():
	try:
		values = [ as7341.channel_415nm, as7341.channel_445nm, as7341.channel_480nm, as7341.channel_515nm, as7341.channel_555nm, as7341.channel_590nm, as7341.channel_630nm, as7341.channel_680nm, as7341.channel_clear, as7341.channel_nir ]
	except:
		values = [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0  ]
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
	return ", %d, %d, %d, %d, %d, %d, %d, %d, %d, %d" % (values[0], values[1], values[2], values[3], values[4], values[5], values[6], values[7], values[8], values[9])

def compact_output():
	print(measure_string())

def verbose_output():
	print("415nm/Violet  %s" % bar_graph(as7341.channel_415nm))
	print("445nm/Indigo  %s" % bar_graph(as7341.channel_445nm))
	print("480nm/Blue    %s" % bar_graph(as7341.channel_480nm))
	print("515nm/Cyan    %s" % bar_graph(as7341.channel_515nm))
	print("555nm/Green   %s" % bar_graph(as7341.channel_555nm))
	print("590nm/Yellow  %s" % bar_graph(as7341.channel_590nm))
	print("630nm/Orange  %s" % bar_graph(as7341.channel_630nm))
	print("680nm/Red     %s" % bar_graph(as7341.channel_680nm))
	print("Clear         %s" % bar_graph(as7341.channel_clear))
	print("Near-IR (NIR) %s" % bar_graph(as7341.channel_nir))
	print("------------------------------------------------")

if __name__ == "__main__":
	i2c = busio.I2C(board.SCL1, board.SDA1)
	#i2c = board.I2C()
	setup(i2c)
	while test_if_present():
		compact_output()
		sleep(1)

