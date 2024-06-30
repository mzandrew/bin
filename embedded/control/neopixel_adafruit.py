# last updated 2021-09-12 by mza

import board
import neopixel
from DebugInfoWarningError24 import debug, info, warning, error, debug2, debug3, set_verbosity, create_new_logfile_with_string_embedded, flush

def setup_neopixel():
	global pixel
	try:
		pixel = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0.01, auto_write=True)
	except:
		warning("can't find neopixel")
		return False
	return True

def set_color(red, green, blue):
	try:
		pixel.fill((red, green, blue))
	except:
		pass

