# written 2021-09-10 by mza
# last updated 2021-09-19 by mza

# to install on a circuitpython device:
# cp DebugInfoWarningError24.py pcf8523_adafruit.py microsd_adafruit.py neopixel_adafruit.py pct2075_adafruit.py bh1750_adafruit.py ltr390_adafruit.py vcnl4040_adafruit.py as7341_adafruit.py tsl2591_adafruit.py ds18b20_adafruit.py /media/circuitpython/
# cp solar_water_heater.py /media/circuitpython/code.py
# cd ~/build/adafruit-circuitpython/bundle/lib
# rsync -r adafruit_register adafruit_sdcard.mpy adafruit_pct2075.mpy adafruit_bh1750.mpy adafruit_vcnl4040.mpy adafruit_ltr390.mpy neopixel.mpy adafruit_as7341.mpy adafruit_pcf8523.mpy adafruit_tsl2591.mpy adafruit_onewire adafruit_ds18x20.mpy /media/circuitpython/lib/

should_use_RTC = True
should_use_sdcard = True

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
from DebugInfoWarningError24 import debug, info, warning, error, debug2, debug3, set_verbosity, create_new_logfile_with_string_embedded, flush

header_string = "date/time"
dir = "/logs"

def print_compact(string):
	try:
		date = time.strftime("%Y-%m-%d+%X, ")
	except:
		try:
			date = pcf8523_adafruit.get_timestring1() + ", "
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
	if should_use_sdcard:
		sdcard_is_available = microsd_adafruit.setup_sdcard_for_logging_data(dir)
	else:
		sdcard_is_available = False
	if not sdcard_is_available:
		dir = "/"
	if RTC_is_available:
		create_new_logfile_with_string_embedded(dir, "solar_water_heater", pcf8523_adafruit.get_timestring2())
	else:
		create_new_logfile_with_string_embedded(dir, "solar_water_heater")
	try:
		i2c_address = bh1750_adafruit.setup(i2c)
		prohibited_addresses.append(i2c_address)
		bh1750_is_available = True
		header_string += ", bh1750-lux"
	except:
		warning("bh1750 not found")
		bh1750_is_available = False
	try:
		i2c_address = ltr390_adafruit.setup(i2c)
		prohibited_addresses.append(i2c_address)
		ltr390_is_available = True
		header_string += ", ltr390-uvs, ltr390-light, ltr390-uvi, ltr390-lux"
	except:
		warning("ltr390 not found")
		ltr390_is_available = False
	try:
		i2c_address = vcnl4040_adafruit.setup(i2c)
		prohibited_addresses.append(i2c_address)
		vcnl4040_is_available = True
		header_string += ", vcnl4040-proximity, vcnl4040-lux"
	except:
		warning("vcnl4040 not found")
		vcnl4040_is_available = False
	try:
		i2c_address = as7341_adafruit.setup(i2c)
		prohibited_addresses.append(i2c_address)
		as7341_is_available = True
		header_string += ", as7341-415nm, as7341-445nm, as7341-480nm, as7341-515nm, as7341-555nm, as7341-590nm, as7341-630nm, as7341-680nm"
	except:
		warning("as7341 not found")
		as7341_is_available = False
	try:
		i2c_address = tsl2591_adafruit.setup(i2c)
		prohibited_addresses.append(i2c_address)
		tsl2591_is_available = True
		header_string += ", tsl2591.lux, tsl2591.visible, tsl2591.infrared, tsl2591.full_spectrum"
	except:
		warning("tsl2591 not found")
		tsl2591_is_available = False
	try:
		ow_bus = OneWireBus(board.D5)
		ds18b20_adafruit.setup(ow_bus)
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
		addresses = pct2075_adafruit.setup(i2c, prohibited_addresses)
		#info("pct2075" + str(addresses))
		header_string += ", pct2075-C"
	except:
		error("pct2075 not found")
	#gnuplot> set key autotitle columnheader
	#gnuplot> set style data lines
	#gnuplot> plot for [i=1:14] "solar_water_heater.log" using 0:i
	print_header()
	while pct2075_adafruit.test_if_present():
		neopixel_adafruit.set_color(255, 0, 0)
		string = ""
		#gnuplot> plot for [i=2:2] "solar_water_heater.log" using 0:i
		string += pct2075_adafruit.measure_string()
		if bh1750_is_available:
			#gnuplot> plot for [i=3:3] "solar_water_heater.log" using 0:i
			string += bh1750_adafruit.measure_string()
		if ltr390_is_available:
			#gnuplot> plot for [i=4:7] "solar_water_heater.log" using 0:i
			string += ltr390_adafruit.measure_string()
		if vcnl4040_is_available:
			#gnuplot> plot for [i=8:9] "solar_water_heater.log" using 0:i
			string += vcnl4040_adafruit.measure_string()
		if as7341_is_available:
			#gnuplot> plot for [i=10:17] "solar_water_heater.log" using 0:i
			string += as7341_adafruit.measure_string()
		if tsl2591_is_available:
			string += tsl2591_adafruit.measure_string()
		if ds18b20_is_available:
			string += ds18b20_adafruit.measure_string()
		print_compact(string)
		flush()
		neopixel_adafruit.set_color(0, 255, 0)
		time.sleep(1)
	info("pct2075 not available; cannot continue")

