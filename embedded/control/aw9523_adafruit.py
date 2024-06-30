# written 2022-11-19 by mza
# with help from https://learn.adafruit.com/adafruit-aw9523-gpio-expander-and-led-driver/python-circuitpython
# last updated 2022-11-19 by mza

import math
import time
import board
import busio
import digitalio
import adafruit_aw9523

VALMIN = 0
VALMAX = 128

def setup(i2c):
	global ex
	ex = adafruit_aw9523.AW9523(i2c)
	ex.LED_modes = 0xffff
	ex.directions = 0xffff

def demo_sawtooth():
	value = VALMIN
	while True:
		for i in range(16):
			ex.set_constant_current(i, value%256)
		#print(str(value))
		value += 1
		if VALMAX<value:
			value = VALMIN
		time.sleep(0.1)

def demo_sine():
	angle_increment = 0.02
	PI = 3.141592
	angle = 3*PI/2
	while True:
		value = (VALMAX+VALMIN)/2 + (VALMAX-VALMIN)/2 * math.sin(angle)
		value = int(value)
		for i in range(16):
			ex.set_constant_current(i, value%256)
		#print(str(value))
		angle += angle_increment
		time.sleep(0.025)

if __name__ == "__main__":
	i2c = busio.I2C(board.SCL1, board.SDA1)
	setup(i2c)
	#demo_sawtooth()
	demo_sine()

