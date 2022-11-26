# written 2022-10-29 by mza
# based on neopixel_clockface.py
# last updated 2022-11-25 by mza

# to install:
# cd lib
# rsync -r adafruit_as7341.mpy neopixel.mpy adafruit_minimqtt simpleio.mpy adafruit_esp32spi adafruit_register adafruit_io adafruit_requests.mpy adafruit_bus_device /media/mza/CIRCUITPY/lib/
# cd ..
# rsync -av *.py /media/mza/CIRCUITPY/
# cp -a roofDAQ2.py /media/mza/CIRCUITPY/code.py; sync

import time
import re
import board
import busio
import neopixel
import as7341_adafruit
import airlift
from DebugInfoWarningError24 import debug, info, warning, error, debug2, debug3, set_verbosity, create_new_logfile_with_string_embedded, flush

my_wifi_name = "roof2"
my_adafruit_io_prefix = "roof2"
N = 60 # average this many sensor readings before acting on it
should_use_RTC = False

eta = 1.0/512.0

def setup():
	header_string = ""
	global i2c
	try:
		i2c = busio.I2C(board.SCL1, board.SDA1)
		string = "using I2C1 "
	except (KeyboardInterrupt, ReloadException):
		raise
	except:
		#i2c = busio.I2C(board.SCL, board.SDA)
		i2c = board.I2C()
		string = "using I2C0 "
	info(string)
	global as7341_is_available
	as7341_is_available = False
	try:
		i2c_address = as7341_adafruit.setup(i2c, N)
		as7341_is_available = True
		header_string += ", as7341-415nm, as7341-445nm, as7341-480nm, as7341-515nm, as7341-555nm, as7341-590nm, as7341-630nm, as7341-680nm, as7341-clear, as7341-nir"
	except:
		warning("as7341 not found")
	global RTC_is_available
	RTC_is_available = False
	if should_use_RTC:
		try:
			#i2c_address = pcf8523_adafruit.setup(i2c)
			i2c_address = ds3231_adafruit.setup(i2c)
			RTC_is_available = True
		except (KeyboardInterrupt, ReloadException):
			raise
		except:
			RTC_is_available = False
	if RTC_is_available:
		string = ds3231_adafruit.get_timestring2()
		info(string)
	global airlift_is_available
	airlift_is_available = airlift.setup_wifi(my_wifi_name)
	if 0:
		if airlift_is_available:
			airlift.update_time_from_server()
	if airlift_is_available:
		header_string += ", rssi-dB"
		airlift.setup_feed(my_adafruit_io_prefix + "-415nm")
		time.sleep(1)
		airlift.setup_feed(my_adafruit_io_prefix + "-445nm")
		time.sleep(1)
		airlift.setup_feed(my_adafruit_io_prefix + "-480nm")
		time.sleep(1)
		airlift.setup_feed(my_adafruit_io_prefix + "-515nm")
		time.sleep(1)
		airlift.setup_feed(my_adafruit_io_prefix + "-555nm")
		time.sleep(1)
		airlift.setup_feed(my_adafruit_io_prefix + "-590nm")
		time.sleep(1)
		airlift.setup_feed(my_adafruit_io_prefix + "-630nm")
		time.sleep(1)
		airlift.setup_feed(my_adafruit_io_prefix + "-680nm")
		time.sleep(1)
		airlift.setup_feed(my_adafruit_io_prefix + "-clear")
		time.sleep(1)
		airlift.setup_feed(my_adafruit_io_prefix + "-nir")
		time.sleep(1)
		airlift.setup_feed(my_adafruit_io_prefix + "-rssi")
		time.sleep(1)
	info(header_string)

def loop():
	global n
	string = ""
	if as7341_is_available:
		string += as7341_adafruit.measure_string()
		as7341_adafruit.get_values()
	string += airlift.measure_string()
	info(string)
	n += 1
	if 0==n%N:
		if as7341_is_available:
			as7341_adafruit.show_average_values()
			if airlift_is_available:
				try:
					airlift.post_data(my_adafruit_io_prefix + "-415nm", as7341_adafruit.get_average_values()[0])
					airlift.post_data(my_adafruit_io_prefix + "-445nm", as7341_adafruit.get_average_values()[1])
					airlift.post_data(my_adafruit_io_prefix + "-480nm", as7341_adafruit.get_average_values()[2])
					airlift.post_data(my_adafruit_io_prefix + "-515nm", as7341_adafruit.get_average_values()[3])
					airlift.post_data(my_adafruit_io_prefix + "-555nm", as7341_adafruit.get_average_values()[4])
					airlift.post_data(my_adafruit_io_prefix + "-590nm", as7341_adafruit.get_average_values()[5])
					airlift.post_data(my_adafruit_io_prefix + "-630nm", as7341_adafruit.get_average_values()[6])
					airlift.post_data(my_adafruit_io_prefix + "-680nm", as7341_adafruit.get_average_values()[7])
					airlift.post_data(my_adafruit_io_prefix + "-clear", as7341_adafruit.get_average_values()[8])
					airlift.post_data(my_adafruit_io_prefix + "-nir", as7341_adafruit.get_average_values()[9])
				except:
					warning("couldn't post data for as7341")
			#airlift.post_data(my_adafruit_io_prefix + "-rssi", airlift.get_rssi())
			airlift.show_average_values()
			airlift.post_data(my_adafruit_io_prefix + "-rssi", airlift.get_average_values()[0])
	#parse_RTC()
	time.sleep(1)

if __name__ == "__main__":
	setup()
	info("")
	n = 0
	while True:
		loop()

