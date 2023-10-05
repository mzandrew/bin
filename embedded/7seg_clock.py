#!/usr/bin/env python3

# written 2023-10-05 by mza
# last updated 2023-10-05 by mza

# to install:
# cp -ar adafruit_display_text adafruit_ht16k33 /media/mza/CIRCUITPY/lib/
# cp -a display_adafruit.py DebugInfoWarningError24.py /media/mza/CIRCUITPY/
# cp -a 7seg_clock.py /media/mza/CIRCUITPY/code.py; sync

import board
import busio
import display_adafruit

if __name__ == "__main__":
	#i2c = board.I2C()
	i2c = busio.I2C(board.SCL1, board.SDA1)
	display_adafruit.setup_7seg_numeric_backpack_4(i2c)
	display_adafruit.update_string_on_7seg_numeric_backpack_4("4:20")

