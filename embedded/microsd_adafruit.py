# last updated 2021-09-12 by mza

import adafruit_sdcard
import storage
import board
import busio
import digitalio
from DebugInfoWarningError24 import debug, info, warning, error, debug2, debug3, set_verbosity, create_new_logfile_with_string_embedded, flush

def setup_sdcard_for_logging_data(dir):
	try:
		spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
		#cs = digitalio.DigitalInOut(board.D6)
		cs = digitalio.DigitalInOut(board.D10) # adalogger feather
		sdcard = adafruit_sdcard.SDCard(spi, cs)
		vfs = storage.VfsFat(sdcard)
		storage.mount(vfs, dir) # this does NOT need an empty dir to mount on
		#with open("/logs/test.txt", "w") as f:
		#	f.write("Hello, World!\r\n")
	except:
		error("unable to find/mount sdcard")
		return False
	return True

