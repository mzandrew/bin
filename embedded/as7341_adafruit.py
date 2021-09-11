# https://learn.adafruit.com/adafruit-as7341-10-channel-light-color-sensor-breakout/python-circuitpython
# SPDX-FileCopyrightText: 2020 Bryan Siepert, written for Adafruit Industries
# SPDX-License-Identifier: MIT
# last updated 2021-09-11 by mza
import time
import board
import adafruit_as7341

def setup(i2c):
	global sensor
	sensor = adafruit_as7341.AS7341(i2c)

def test_if_present():
	try:
		sensor.channel_415nm
	except:
		return False
	return True

def bar_graph(read_value):
	scaled = int(read_value / 1000)
	return "[%5d] " % read_value + (scaled * "*")

def measure_string():
	return ", %d, %d, %d, %d, %d, %d, %d, %d" % (sensor.channel_415nm, sensor.channel_445nm, sensor.channel_480nm, sensor.channel_515nm, sensor.channel_555nm, sensor.channel_590nm, sensor.channel_630nm, sensor.channel_680nm)

def compact_output():
	print(measure_string)

def verbose_output():
	print("F1 - 415nm/Violet  %s" % bar_graph(sensor.channel_415nm))
	print("F2 - 445nm/Indigo  %s" % bar_graph(sensor.channel_445nm))
	print("F3 - 480nm/Blue    %s" % bar_graph(sensor.channel_480nm))
	print("F4 - 515nm/Cyan    %s" % bar_graph(sensor.channel_515nm))
	print("F5 - 555nm/Green   %s" % bar_graph(sensor.channel_555nm))
	print("F6 - 590nm/Yellow  %s" % bar_graph(sensor.channel_590nm))
	print("F7 - 630nm/Orange  %s" % bar_graph(sensor.channel_630nm))
	print("F8 - 680nm/Red     %s" % bar_graph(sensor.channel_680nm))
	#print("Clear              %s" % bar_graph(sensor.channel_clear))
	#print("Near-IR (NIR)      %s" % bar_graph(sensor.channel_nir))
	print("------------------------------------------------")

if __name__ == "__main__":
	i2c = busio.I2C(board.SCL1, board.SDA1)
	#i2c = board.I2C()
	setup(i2c)
	while test_if_present():
		compact_output()
		sleep(1)

