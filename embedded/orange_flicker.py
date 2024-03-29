# written 2022-10-29 by mza
# with help from https://learn.adafruit.com/adafruit-circuit-playground-express/circuitpython-neopixel
# and from https://learn.adafruit.com/adafruit-circuit-playground-express/circuitpython-digital-in-out
# based on purple.py
# last updated 2023-11-01 by mza

# circuit playground bluefruit requires new bootloader and the neopixel lib:
# pip3 install --user adafruit-nrfutil
# adafruit-nrfutil --verbose dfu serial --package ~/Downloads/adafruit/circuitplayground_nrf52840_bootloader-0.8.0_s140_6.1.1.zip -p /dev/ttyACM0 -b 115200 --singlebank --touch 1200
# cp -a neopixel.mpy /media/mza/CIRCUITPY/lib/; sync

import time
import board
import random
import neopixel
import digitalio

#brightness = 0.1 # dim
#brightness = 0.25 # medium
brightness = 1.0 # avert your eyes!
pixel = neopixel.NeoPixel(board.NEOPIXEL, 10, brightness=brightness, auto_write=True)
BLACK = (0, 0, 0)
#red_to_green = 6 # good for pumpkin orange
red_to_green = 2 # good for yellow/golden sparkle
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

