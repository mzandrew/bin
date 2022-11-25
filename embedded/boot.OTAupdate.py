# written 2022-11-24 by mza
# idea from https://github.com/KTibow/fridge/blob/main/boot.py
# with help from https://learn.adafruit.com/pico-w-wifi-with-circuitpython/pico-w-basic-wifi-test
# last updated 2022-11-25 by mza

should_download_the_files = True
should_write_the_files = True

# to install:
# rsync -r adafruit_minimqtt simpleio.mpy adafruit_esp32spi adafruit_register adafruit_sdcard.mpy adafruit_io adafruit_requests.mpy /media/mza/CIRCUITPY/lib/
# rsync -a generic.py airlift.py DebugInfoWarningError24.py /media/mza/CIRCUITPY/
# cp -a boot.OTAupdate.py /media/mza/CIRCUITPY/boot.py; sync

import sys
import re
import storage
import os
import board
import digitalio

print("")
print("boot.py started")

OTAjumper = digitalio.DigitalInOut(board.GP17)
OTAjumper.pull = digitalio.Pull.UP

if OTAjumper.value:
	print("no jumper installed between GP17 and GND")
	print("not doing OTAupdate")
	print("boot.py quitting")
	sys.exit(0)
else:
	print("jumper installed between GP17 and GND")
	print("boot.py attempting OTA update...")

try:
	import generic
except:
	print("can't import generic")
	sys.exit(1)

generic.collect_garbage()
#generic.show_memory_difference()

try:
	from DebugInfoWarningError24 import debug, info, warning, error, debug2, debug3, set_verbosity, create_new_logfile_with_string_embedded, flush # uses 1k
except:
	print("can't import DebugInfoWarningError24")
	sys.exit(2)

generic.collect_garbage()
#generic.show_memory_difference()

try:
	import airlift # uses 15k
except:
	error("can't import airlift")
	sys.exit(3)

generic.collect_garbage()
#generic.show_memory_difference()

my_wifi_name = "OTAboot.py"
#if board_id=="raspberry_pi_pico_w":
should_use_airlift = True
use_built_in_wifi = False
#FEATHER_ESP32S2 = True

def hex(number, width=1):
	return "%0*x" % (width, number)

def format_MAC(MAC):
	string = ""
	for byte in MAC:
		if len(string):
			string += "-"
		string += hex(byte, 2)
	return string

if should_use_airlift:
	if use_built_in_wifi:
		airlift_is_available = airlift.setup_wifi()
	else:
		try:
			import ipaddress
		except:
			error("can't import ipaddress")
		try:
			import wifi
		except:
			error("can't import wifi")
		try:
			import socketpool
		except:
			error("can't import socketpool")
		try:
			import adafruit_requests
		except:
			error("can't import adafruit_requests")
		try:
			import ssl
		except:
			error("can't import ssl")
		try:
			wifi.radio.hostname = my_wifi_name
			match = re.search("^[8]", os.uname().release)
			if match:
				wifi.radio.connect(ssid=os.getenv('CIRCUITPY_WIFI_SSID'), password=os.getenv('CIRCUITPY_WIFI_PASSWORD')) # os.getenv is a circuitpython 8 thing (see file .env)
			else:
				import secrets
				wifi.radio.connect(ssid=secrets.secrets["ssid"], password=secrets.secrets["password"])
			mac_address = list(wifi.radio.mac_address)
			info("MAC: " + format_MAC(mac_address))
			info("My IP address is " + str(wifi.radio.ipv4_address))
		except:
			error("can't connect to wifi")
			sys.exit(4)
		try:
			pool = socketpool.SocketPool(wifi.radio)
		except:
			error("can't create socket pool")
			sys.exit(5)
		try:
			requests = adafruit_requests.Session(pool, ssl.create_default_context())
		except:
			error("can't setup requests")
			sys.exit(6)
		#spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
		#airlift_is_available = airlift.setup_airlift(my_wifi_name, spi, board.D13, board.D11, board.D12) # feather
else:
	error("no wifi capability; can't update")
	sys.exit(7)

#generic.show_memory_difference() # 12k

if should_write_the_files:
	try:
		storage.remount("/", False)
	except:
		error("can't remount / when visible via USB")
		sys.exit(8)
	create_new_logfile_with_string_embedded("/", "logfile.txt")

try:
	import microsd_adafruit
except:
	error("can't import microsd_adafruit")
	sys.exit(9)

#generic.show_memory_difference()

generic.collect_garbage()
#generic.show_memory_situation()

files_list = [ "boot.OTAupdate.py" ]
files_list += [ "airlift.py", "generic.py", "DebugInfoWarningError24.py", "boxcar.py" ]
files_list += [ "am2320_adafruit.py", "as7341_adafruit.py", "aw9523_adafruit.py", "bh1750_adafruit.py", "bme680_adafruit.py", "display_adafruit.py", "ds18b20_adafruit.py", "ds3231_adafruit.py", "gps_adafruit.py", "ina260_adafruit.py", "ltr390_adafruit.py", "max31865_adafruit.py", "microsd_adafruit.py", "neopixel_adafruit.py", "pcf8523_adafruit.py", "pct2075_adafruit.py", "pm25_adafruit.py", "sht31d_adafruit.py", "si5351_adafruit.py", "tsl2591_adafruit.py", "vcnl4040_adafruit.py" ]
#files_list += [ "purple.py", "orange_flicker.py", "console.py" ]
# "ble_adafruit.py", 
for filename in files_list:
	if should_download_the_files:
		try:
			file_contents = requests.get(f"https://raw.githubusercontent.com/mzandrew/bin/master/embedded/" + filename).text
			info(filename + " " + str(len(file_contents)) + " bytes")
			try:
				#info(file_contents)
				if 0<len(file_contents) and filename != "boot.py":
					if should_write_the_files:
						with open(filename, "w") as code:
							code.write(file_contents)
							code.flush()
			except:
				error("couldn't write " + filename)
		except:
			error("couldn't download " + filename)
	try:
		microsd_adafruit.list_file("", filename)
	except:
		warning("can't find file " + filename)

info("OTA update successful")
storage.enable_usb_drive()
storage.remount("/", readonly=True)
sys.exit(0)

