# written 2021-09-10 by mza
# last updated 2021-09-12 by mza

# to install on a circuitpython device:
# cp DebugInfoWarningError24.py pcf8523_adafruit.py microsd_adafruit.py neopixel_adafruit.py pct2075_adafruit.py bh1750_adafruit.py ltr390_adafruit.py vcnl4040_adafruit.py as7341_adafruit.py /media/circuitpython/
# cp solar_water_heater.py /media/circuitpython/code.py
# cd ~/build/adafruit-circuitpython/bundle/lib
# rsync -r adafruit_register adafruit_sdcard.mpy adafruit_pct2075.mpy adafruit_bh1750.mpy adafruit_vcnl4040.mpy adafruit_ltr390.mpy neopixel.mpy adafruit_as7341.mpy adafruit_pcf8523.mpy /media/circuitpython/lib/

should_use_RTC = True
should_use_sdcard = True
dir = "/logs"

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
from DebugInfoWarningError24 import debug, info, warning, error, debug2, debug3, set_verbosity, create_new_logfile_with_string_embedded, flush

def print_compact(string):
	try:
		date = time.strftime("%Y-%m-%d+%X, ")
	except:
		try:
			date = pcf8523_adafruit.get_timestring1() + ", "
		except:
			date = ""
	info("%s%s" % (date, string))

if __name__ == "__main__":
	try:
		i2c = busio.I2C(board.SCL1, board.SDA1)
		info("using I2C1")
	except:
		i2c = busio.I2C(board.SCL, board.SDA)
		info("using I2C0")
	if should_use_RTC:
		RTC_is_available = pcf8523_adafruit.setup(i2c)
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
		pct2075_adafruit.setup(i2c)
	except:
		error("pct2075 not found")
	try:
		bh1750_adafruit.setup(i2c)
		bh1750_is_available = True
	except:
		warning("bh1750 not found")
		bh1750_is_available = False
	try:
		ltr390_adafruit.setup(i2c)
		ltr390_is_available = True
	except:
		warning("ltr390 not found")
		ltr390_is_available = False
	try:
		vcnl4040_adafruit.setup(i2c)
		vcnl4040_is_available = True
	except:
		warning("vcnl4040 not found")
		vcnl4040_is_available = False
	try:
		as7341_adafruit.setup(i2c)
		as7341_is_available = True
	except:
		warning("as7341 not found")
		as7341_is_available = False
	try:
		neopixel_is_available = neopixel_adafruit.setup_neopixel()
	except:
		warning("error setting up neopixel")
	while pct2075_adafruit.test_if_present():
		neopixel_adafruit.set_color(255, 0, 0)
		string = ""
		string += pct2075_adafruit.measure_string()
		if bh1750_is_available:
			string += bh1750_adafruit.measure_string()
		if ltr390_is_available:
			string += ltr390_adafruit.measure_string()
		if vcnl4040_is_available:
			string += vcnl4040_adafruit.measure_string()
		if as7341_is_available:
			string += as7341_adafruit.measure_string()
		print_compact(string)
		flush()
		neopixel_adafruit.set_color(0, 255, 0)
		time.sleep(1)

