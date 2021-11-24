# written 2021-09-10 by mza
# last updated 2021-11-24 by mza

# to install on a circuitpython device:
# cp -a anemometer.py boxcar.py airlift.py DebugInfoWarningError24.py pcf8523_adafruit.py microsd_adafruit.py neopixel_adafruit.py pct2075_adafruit.py bh1750_adafruit.py ltr390_adafruit.py vcnl4040_adafruit.py as7341_adafruit.py tsl2591_adafruit.py ds18b20_adafruit.py sht31d_adafruit.py /media/circuitpython/
# cp -a solar_water_heater.py /media/circuitpython/code.py
# cd ~/build/adafruit-circuitpython/bundle/lib
# rsync -r adafruit_register adafruit_sdcard.mpy adafruit_pct2075.mpy adafruit_bh1750.mpy adafruit_vcnl4040.mpy adafruit_ltr390.mpy neopixel.mpy adafruit_as7341.mpy adafruit_pcf8523.mpy adafruit_tsl2591.mpy adafruit_onewire adafruit_ds18x20.mpy /media/circuitpython/lib/

should_use_RTC = True
should_use_sdcard = True
header_string = "date/time"
dir = "/logs"
N = 64
delay = 0.7
if 0:
	feed = "test"
	should_use_airlift = False
else:
	feed = "sun"
	should_use_airlift = True

import sys
import time
import board
import busio
import pct2075_adafruit
import bh1750_adafruit
import ltr390_adafruit
import vcnl4040_adafruit
import as7341_adafruit
import pcf8523_adafruit
import microsd_adafruit
import neopixel_adafruit
import ds18b20_adafruit
import tsl2591_adafruit
import anemometer
import sht31d_adafruit
import airlift
from DebugInfoWarningError24 import debug, info, warning, error, debug2, debug3, set_verbosity, create_new_logfile_with_string_embedded, flush

def print_compact(string):
	try:
		date = time.strftime("%Y-%m-%d+%X")
	except:
		try:
			date = pcf8523_adafruit.get_timestring1()
		except:
			date = ""
	info("%s%s" % (date, string))

def print_header():
	info("" + header_string)

if __name__ == "__main__":
	try:
		i2c = busio.I2C(board.SCL1, board.SDA1)
		string = "using I2C1 "
	except:
		i2c = busio.I2C(board.SCL, board.SDA)
		string = "using I2C0 "
	#i2c.try_lock()
	#i2c_list = i2c.scan()
	#i2c.unlock()
	#info(string + str(i2c_list))
	prohibited_addresses = []
	if should_use_RTC:
		i2c_address = pcf8523_adafruit.setup(i2c)
		prohibited_addresses.append(i2c_address)
		RTC_is_available = True
	else:
		RTC_is_available = False
	spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
	if should_use_sdcard:
		sdcard_is_available = microsd_adafruit.setup_sdcard_for_logging_data(spi, dir)
	else:
		sdcard_is_available = False
	if not sdcard_is_available:
		dir = "/"
	if RTC_is_available:
		create_new_logfile_with_string_embedded(dir, "solar_water_heater", pcf8523_adafruit.get_timestring2())
	else:
		create_new_logfile_with_string_embedded(dir, "solar_water_heater")
	try:
		i2c_address = bh1750_adafruit.setup(i2c, N)
		prohibited_addresses.append(i2c_address)
		bh1750_is_available = True
		header_string += ", bh1750-lux"
	except:
		warning("bh1750 not found")
		bh1750_is_available = False
	try:
		i2c_address = ltr390_adafruit.setup(i2c, N)
		prohibited_addresses.append(i2c_address)
		ltr390_is_available = True
		header_string += ", ltr390-uvs, ltr390-uvi, ltr390-light, ltr390-lux"
	except:
		warning("ltr390 not found")
		ltr390_is_available = False
	try:
		i2c_address = vcnl4040_adafruit.setup(i2c, N)
		prohibited_addresses.append(i2c_address)
		vcnl4040_is_available = True
		header_string += ", vcnl4040-proximity, vcnl4040-lux"
	except:
		warning("vcnl4040 not found")
		vcnl4040_is_available = False
	try:
		i2c_address = as7341_adafruit.setup(i2c, N)
		prohibited_addresses.append(i2c_address)
		as7341_is_available = True
		header_string += ", as7341-415nm, as7341-445nm, as7341-480nm, as7341-515nm, as7341-555nm, as7341-590nm, as7341-630nm, as7341-680nm"
	except:
		warning("as7341 not found")
		as7341_is_available = False
	try:
		i2c_address = tsl2591_adafruit.setup(i2c, N)
		prohibited_addresses.append(i2c_address)
		tsl2591_is_available = True
		header_string += ", tsl2591.lux, tsl2591.infrared, tsl2591.visible, tsl2591.full-spectrum"
	except:
		warning("tsl2591 not found")
		tsl2591_is_available = False
	try:
		ow_bus = OneWireBus(board.D5)
		ds18b20_adafruit.setup(ow_bus, N)
		ds18b20_is_available = True
		header_string += ", ds18b20-C"
	except:
		warning("ds18b20 not found")
		ds18b20_is_available = False
	try:
		neopixel_is_available = neopixel_adafruit.setup_neopixel()
	except:
		warning("error setting up neopixel")
	#info(str(prohibited_addresses)) # disallow treating any devices already discovered as pct2075s
	try:
		anemometer_is_available = anemometer.setup(board.A0, N)
		header_string += ", anemometer-m/s"
	except:
		warning("anemometer not found")
		anemometer_is_available = False
	try:
		i2c_address = sht31d_adafruit.setup(i2c, N)
		prohibited_addresses.append(i2c_address)
		header_string += ", sht31d-C, sht31d-%RH"
		sht31d_is_available = True
	except:
		warning("sht31d not found")
		sht31d_is_available = False
	try:
		addresses = pct2075_adafruit.setup(i2c, prohibited_addresses, N)
		#info("pct2075" + str(addresses))
		header_string += ", pct2075-C"
	except:
		error("pct2075 not found")
		sys.exit(1)
	if should_use_airlift:
		airlift_is_available = airlift.setup_airlift(spi)
	else:
		airlift_is_available = False
	if airlift_is_available:
		airlift.setup_feed(feed)
	#gnuplot> set key autotitle columnheader
	#gnuplot> set style data lines
	#gnuplot> plot for [i=1:14] "solar_water_heater.log" using 0:i
	print_header()
	i = 0
	while pct2075_adafruit.test_if_present():
		#info("")
		#info(str(i))
		neopixel_adafruit.set_color(255, 0, 0)
		string = ""
		if bh1750_is_available:
			#info("bh1750")
			#gnuplot> plot for [i=3:3] "solar_water_heater.log" using 0:i
			string += bh1750_adafruit.measure_string()
		if ltr390_is_available:
			#info("ltr390")
			#gnuplot> plot for [i=4:7] "solar_water_heater.log" using 0:i
			string += ltr390_adafruit.measure_string()
		if vcnl4040_is_available:
			#info("vcnl4040")
			#gnuplot> plot for [i=8:9] "solar_water_heater.log" using 0:i
			string += vcnl4040_adafruit.measure_string()
		if as7341_is_available:
			#info("as7341")
			#gnuplot> plot for [i=8:15] "solar_water_heater.log" using 0:i
			string += as7341_adafruit.measure_string()
		if tsl2591_is_available:
			#info("tsl2591")
			string += tsl2591_adafruit.measure_string()
		if ds18b20_is_available:
			#info("ds18b20")
			string += ds18b20_adafruit.measure_string()
		if anemometer_is_available:
			#info("anemometer")
			string += anemometer.measure_string()
		if sht31d_is_available:
			#info("sht31d")
			string += sht31d.measure_string()
		#info("pct2075")
		#gnuplot> plot for [i=2:2] "solar_water_heater.log" using 0:i
		string += ", " + pct2075_adafruit.measure_string()
		print_compact(string)
		flush()
		neopixel_adafruit.set_color(0, 255, 0)
		i += 1
		if 0==i%N:
			if bh1750_is_available:
				bh1750_adafruit.show_average_values()
			if ltr390_is_available:
				ltr390_adafruit.show_average_values()
			if vcnl4040_is_available:
				vcnl4040_adafruit.show_average_values()
			if as7341_is_available:
				as7341_adafruit.show_average_values()
			if tsl2591_is_available:
				tsl2591_adafruit.show_average_values()
			if ds18b20_is_available:
				ds18b20_adafruit.show_average_values()
			if anemometer_is_available:
				anemometer.show_average_values()
			if sht31d_is_available:
				sht31d_adafruit.show_average_values()
			pct2075_adafruit.show_average_values()
			if airlift_is_available:
				airlift.post_data(bh1750_adafruit.get_average_values()[0])
		neopixel_adafruit.set_color(0, 0, 255)
		time.sleep(delay)
	info("pct2075 not available; cannot continue")

