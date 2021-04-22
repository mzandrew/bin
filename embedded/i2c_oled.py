#!/usr/bin/env python3

# written 2021-04-21 by mza
# last updated 2021-04-21 by mza

import time
import board
import busio
import adafruit_ssd1327
import displayio

def setup_i2c_oled_display(address):
	displayio.release_displays()
	display_bus = displayio.I2CDisplay(i2c, device_address=address)
	global display
	display = adafruit_ssd1327.SSD1327(display_bus, width=128, height=128)

if __name__ == "__main__":
	try:
		setup_i2c_oled_display(0x3d)
	except:
		error("can't initialize ssd1327 display over i2c (address 0x3d)")
		sys.exit(1)
	while True:
		pass
		time.sleep(1)

