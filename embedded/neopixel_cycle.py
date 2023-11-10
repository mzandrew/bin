#!/usr/bin/env python3

# written 2021-04-21 by mza
# with help from https://learn.adafruit.com/adafruit-neopixel-driver-bff/circuitpython
# last updated 2023-11-10 by mza

# to install:
# cp -ar adafruit_pixelbuf.mpy neopixel.mpy /media/mza/CIRCUITPY/lib/
# cp -a neopixel_cycle.py /media/mza/NEO90/code.py; sync

import time
import board
from rainbowio import colorwheel
import neopixel

if 0:
	NUMPIXELS = 1
	PIN = board.NEOPIXEL
else:
	NUMPIXELS = 60
	#NUMPIXELS = 90
	#NUMPIXELS = 120
	#NUMPIXELS = 144
	#NUMPIXELS = 165
	PIN = board.A3

SPEED = 0.001
BRIGHTNESS = 0.2
pixels = neopixel.NeoPixel(PIN, NUMPIXELS, brightness=BRIGHTNESS, auto_write=False)

def rainbow_cycle(wait):
	for color in range(255):
		for pixel in range(NUMPIXELS):
			pixel_index = (pixel * 256 // NUMPIXELS) + color * 5
			pixels[pixel] = colorwheel(pixel_index & 255)
		pixels.show()
		time.sleep(wait)

while True:
    rainbow_cycle(SPEED)

