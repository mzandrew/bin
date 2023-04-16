# last updated 2022-12-03 by mza

import adafruit_sdcard
import adafruit_datetime
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
	except (KeyboardInterrupt, ReloadException):
		raise
	except Exception as message:
		warning("unable to find/mount sdcard: " + str(message))
		return False
	return True

# with help from https://learn.adafruit.com/adafruit-adalogger-featherwing/circuitpython
def list_file(dirname, filename):
	fullname = dirname + "/" + filename
	stats = os.stat(fullname)
	filesize = stats[6]
	modificationdate = stats[8]
	modificationdate = adafruit_datetime.datetime.fromtimestamp(modificationdate).isoformat()
	info('{0:>19} {1:>12} {2:<40}'.format(str(modificationdate), str(filesize), fullname))

def list_files(dirname):
	mylist = []
	for filename in os.listdir(dirname):
		fullname = dirname + "/" + filename
		stats = os.stat(fullname)
		modificationdate = stats[8]
		mylist.append([modificationdate, filename])
	mylist.sort()
	for item in mylist:
		filename = item[1]
		fullname = dirname + "/" + filename
		stats = os.stat(fullname)
		isdir = stats[0] & 0x4000
		if isdir:
			list_files(fullname)
		else:
			list_file(dirname, filename)

def os_path_isfile(dirname, filename):
	#info("checking for file " + filename + "...")
	for file in os.listdir(dirname):
		#info(file)
		match = re.search(filename, file)
		if match:
			#info("match")
			return True
	return False

