# last updated 2022-08-25 by mza

import adafruit_sdcard
import storage
import board
import busio
import digitalio
import os
import re
from DebugInfoWarningError24 import debug, info, warning, error, debug2, debug3, set_verbosity, create_new_logfile_with_string_embedded, flush

#spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
def setup_sdcard_for_logging_data(spi, cs_pin, dirname):
	try:
		#cs = digitalio.DigitalInOut(board.D6)
		cs = digitalio.DigitalInOut(cs_pin)
		sdcard = adafruit_sdcard.SDCard(spi, cs)
		vfs = storage.VfsFat(sdcard)
		storage.mount(vfs, dirname) # this does NOT need an empty dir to mount on
		#with open("/logs/test.txt", "w") as f:
		#	f.write("Hello, World!\r\n")
	except:
		warning("unable to find/mount sdcard")
		return False
	return True

# from https://learn.adafruit.com/adafruit-adalogger-featherwing/circuitpython
def print_directory(path):
	for file in os.listdir(path):
		fullname = path + "/" + file
		stats = os.stat(fullname)
		filesize = stats[6]
		isdir = stats[0] & 0x4000
		if isdir:
			print_directory(fullname, tabs + 1)
		else:
			print('{0:>12} {1:<40}'.format(str(filesize), fullname))

def os_path_isfile(dirname, filename):
	info("checking for file " + filename + "...")
	for file in os.listdir(dirname):
		info(file)
		match = re.search(filename, file)
		if match:
			info("match")
			return True
	return False

