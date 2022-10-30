# written 2022-10-29 by mza
# with help from https://learn.adafruit.com/adafruit-circuit-playground-express/circuitpython-neopixel
# and from https://learn.adafruit.com/adafruit-circuit-playground-express/circuitpython-digital-in-out
# based on purple.py
# last updated 2022-10-30 by mza

import time
import board
import random
import neopixel
import digitalio

#brightness = 0.1
brightness = 1.0 # avert your eyes!
pixel = neopixel.NeoPixel(board.NEOPIXEL, 10, brightness=brightness, auto_write=True)
BLACK = (0, 0, 0)
red_to_green = 6
green_max = 255 // red_to_green
#value = green_max
#ORANGE = (red_to_green*value, value, 0)
switch = digitalio.DigitalInOut(board.SLIDE_SWITCH)
switch.direction = digitalio.Direction.INPUT
switch.pull = digitalio.Pull.UP

while True:
	if switch.value:
		#pixel.fill(ORANGE)
		for i in range(10):
			value = random.randrange(0, green_max)
			pixel[i] = (red_to_green*value, value, 0)
	else:
		pixel.fill(BLACK)
	time.sleep(0.05)

