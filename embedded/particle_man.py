# written 2021-12-26 by mza
# last updated 2021-12-26 by mza

# to install on a circuitpython device:
# rsync -av *.py /media/circuitpython/
# cp -a particle_man.py /media/circuitpython/code.py
# cd ~/build/adafruit-circuitpython/bundle/lib
# rsync -r adafruit_register neopixel.mpy adafruit_pm25 adafruit_io adafruit_esp32spi adafruit_requests.mpy /media/circuitpython/lib/

header_string = "date/time"
dir = "/logs"
should_use_airlift = True
N = 64
use_built_in_wifi = True
delay_between_acquisitions = 3.0
delay_between_posting_and_next_acquisition = 1.0

import sys
import time
import atexit
import board
import busio
import pwmio
import simpleio
#from adafruit_onewire.bus import OneWireBus
#import pct2075_adafruit
#import bh1750_adafruit
#import ltr390_adafruit
#import vcnl4040_adafruit
#import as7341_adafruit
#import pcf8523_adafruit
#import microsd_adafruit
import neopixel_adafruit
import pm25_adafruit
#import ds18b20_adafruit
#import tsl2591_adafruit
#import anemometer
#import sht31d_adafruit
import airlift
#import gps_adafruit
from DebugInfoWarningError24 import debug, info, warning, error, debug2, debug3, set_verbosity, create_new_logfile_with_string_embedded, flush

def print_header():
	info("" + header_string)

def print_compact(string):
	try:
		date = time.strftime("%Y-%m-%d+%X")
	except:
		try:
			date = pcf8523_adafruit.get_timestring1()
		except:
			try:
				date = gps_adafruit.get_time()
			except:
				date = ""
	info("%s%s" % (date, string))

if __name__ == "__main__":
	try:
		i2c = busio.I2C(board.SCL1, board.SDA1)
		string = "using I2C1 "
	except:
		i2c = busio.I2C(board.SCL, board.SDA)
		string = "using I2C0 "
	try:
		i2c_address = pm25_adafruit.setup(i2c, N)
		pm25_is_available = True
		header_string += ", pm1.0s, pm2.5s, pm10.0s, pm1.0e, pm2.5e, pm10.0e, 0.3um, 0.5um, 1.0um, 2.5um, 5.0um, 10.0um"
	except:
		warning("pm25 not found")
		pm25_is_available = False
	if should_use_airlift:
		if use_built_in_wifi:
			airlift_is_available = airlift.setup_wifi()
		else:
			airlift_is_available = airlift.setup_airlift(spi, board.D13, board.D11, board.D12)
		if airlift_is_available:
			info("airlift is available")
			header_string += ", RSSI-dB"
	else:
		info("airlift is NOT available")
		airlift_is_available = False
	if 0:
		if airlift_is_available:
			airlift.update_time_from_server()
	#gnuplot> set key autotitle columnheader
	#gnuplot> set style data lines
	#gnuplot> plot for [i=1:14] "solar_water_heater.log" using 0:i
	print_header()
	i = 0
	while pm25_adafruit.test_if_present():
		#info("")
		#info(str(i))
		neopixel_adafruit.set_color(255, 0, 0)
		string = ""
		if pm25_is_available:
			string += pm25_adafruit.measure_string()
		if airlift_is_available:
			string += airlift.measure_string()
		print_compact(string)
		flush()
		neopixel_adafruit.set_color(0, 255, 0)
		i += 1
		if 0==i%N:
			if pm25_is_available:
				pm25_adafruit.show_average_values()
			if airlift_is_available:
				try:
					airlift.post_data("particle10", pm25_adafruit.get_average_values()[8])
				except:
					warning("couldn't post data for pm25")
			info("waiting...")
			time.sleep(delay_between_posting_and_next_acquisition)
		neopixel_adafruit.set_color(0, 0, 255)
		if airlift_is_available:
			if 0==i%86300:
				airlift.update_time_from_server()
		time.sleep(delay_between_acquisitions)
	info("pm25 not available; cannot continue")

