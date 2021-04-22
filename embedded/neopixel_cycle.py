#!/usr/bin/env python3

# written 2021-04-21 by mza
# last updated 2021-04-21 by mza

import time
import board
import neopixel

neopin = board.NEOPIXEL
pixel = neopixel.NeoPixel(neopin, 1, brightness=0.2, auto_write=False)
while True:
	pixel.fill((255, 255, 0))
	pixel.show()
	time.sleep(1.0)
	pixel.fill((255, 0, 255))
	pixel.show()
	time.sleep(1.0)
	pixel.fill((0, 255, 255))
	pixel.show()
	time.sleep(1.0)

