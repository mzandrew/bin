# written 2021-12-26 by mza
# last updated 2023-01-08 by mza

# to install on a circuitpython device:
# rsync -av *.py /media/circuitpython/
# cp -a particle_man.py /media/circuitpython/code.py
# cd ~/build/adafruit-circuitpython/bundle/lib
# rsync -r adafruit_register neopixel.mpy adafruit_pm25 adafruit_io adafruit_esp32spi adafruit_requests.mpy /media/circuitpython/lib/

header_string = "date/time"
dir = "/logs"
should_use_airlift = True
N = 32
delay_between_acquisitions = 16
use_built_in_wifi = True
my_wifi_name = "garage-particle"
my_adafruit_io_prefix = "garage"

import sys
import time
import atexit
import supervisor
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
import generic

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

def main():
	global neopixel_is_available
	try:
		neopixel_is_available = neopixel_adafruit.setup_neopixel()
	except:
		warning("error setting up neopixel")
	if neopixel_is_available:
		neopixel_adafruit.set_color(100, 100, 100)
	global i2c
	try:
		i2c = busio.I2C(board.SCL1, board.SDA1)
		string = "using I2C1 "
	except:
		i2c = busio.I2C(board.SCL, board.SDA)
		string = "using I2C0 "
	global pm25_is_available
	global header_string
	try:
		i2c_address = pm25_adafruit.setup(i2c, N)
		pm25_is_available = True
		header_string += ", pm1.0s, pm2.5s, pm10.0s, pm1.0e, pm2.5e, pm10.0e, 0.3um, 0.5um, 1.0um, 2.5um, 5.0um, 10.0um"
	except:
		warning("pm25 not found")
		pm25_is_available = False
	global airlift_is_available
	if should_use_airlift:
		if use_built_in_wifi:
			airlift_is_available = airlift.setup_wifi(my_wifi_name)
		else:
			airlift_is_available = airlift.setup_airlift(my_wifi_name, spi, board.D13, board.D11, board.D12)
		if airlift_is_available:
			info("airlift is available")
			header_string += ", RSSI-dB"
			airlift.setup_feed(my_adafruit_io_prefix + "-0p3")
			airlift.setup_feed(my_adafruit_io_prefix + "-0p5")
			airlift.setup_feed(my_adafruit_io_prefix + "-1p0")
			airlift.setup_feed(my_adafruit_io_prefix + "-2p5")
			airlift.setup_feed(my_adafruit_io_prefix + "-5p0")
			airlift.setup_feed(my_adafruit_io_prefix + "-10p0")
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
	global i
	i = 0
	while pm25_adafruit.test_if_present():
		loop()
	info("pm25 not available; cannot continue")
	if neopixel_is_available:
		neopixel_adafruit.set_color(0, 255, 255)

def loop():
	#info("")
	#info(str(i))
	if neopixel_is_available:
		neopixel_adafruit.set_color(255, 0, 0)
	string = ""
	if pm25_is_available:
		string += pm25_adafruit.measure_string()
	if airlift_is_available:
		string += airlift.measure_string()
	print_compact(string)
	flush()
	if neopixel_is_available:
		neopixel_adafruit.set_color(0, 255, 0)
	global i
	i += 1
	if 0==i%N:
		if pm25_is_available:
			pm25_adafruit.show_average_values()
		if airlift_is_available:
			try:
				airlift.post_data(my_adafruit_io_prefix + "-0p3", pm25_adafruit.get_average_values()[6])
			except:
				warning("couldn't post 0p3 data for pm25")
			try:
				airlift.post_data(my_adafruit_io_prefix + "-0p5", pm25_adafruit.get_average_values()[7])
			except:
				warning("couldn't post 0p5 data for pm25")
			try:
				airlift.post_data(my_adafruit_io_prefix + "-1p0", pm25_adafruit.get_average_values()[8])
			except:
				warning("couldn't post 1p0 data for pm25")
			try:
				airlift.post_data(my_adafruit_io_prefix + "-2p5", pm25_adafruit.get_average_values()[9])
			except:
				warning("couldn't post 2p5 data for pm25")
			try:
				airlift.post_data(my_adafruit_io_prefix + "-5p0", pm25_adafruit.get_average_values()[10])
			except:
				warning("couldn't post 5p0 data for pm25")
			try:
				airlift.post_data(my_adafruit_io_prefix + "-10p0", pm25_adafruit.get_average_values()[11])
			except:
				warning("couldn't post 10p0 data for pm25")
	if neopixel_is_available:
		neopixel_adafruit.set_color(0, 0, 255)
	if airlift_is_available:
		if 0==i%86300:
			airlift.update_time_from_server()
	time.sleep(delay_between_acquisitions)

if __name__ == "__main__":
	#supervisor.disable_autoreload()
	atexit.register(generic.reset)
	try:
		main()
	except KeyboardInterrupt:
		info("caught ctrl-c")
		flush()
		atexit.unregister(generic.reset)
		sys.exit(0)
	except ReloadException:
		info("reload exception")
		flush()
		atexit.unregister(generic.reset)
		time.sleep(1)
		supervisor.reload()
	info("leaving program...")
	flush()
	generic.reset()

