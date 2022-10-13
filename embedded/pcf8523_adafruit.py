# last updated 2022-01-08 by mza

import time
import adafruit_pcf8523
from DebugInfoWarningError24 import debug, info, warning, error, debug2, debug3, set_verbosity, create_new_logfile_with_string_embedded, flush

def setup(i2c):
	global rtc
	try:
		rtc = adafruit_pcf8523.PCF8523(i2c)
		rtc.calibration = -30 # -30 * 4.34 ppm (to compensate for +130 ppm error)
		# https://github.com/adafruit/Adafruit_CircuitPython_PCF8523/blob/main/adafruit_pcf8523.py
		# https://www.nxp.com/docs/en/data-sheet/PCF8523.pdf
		#info(get_timestring1())
		if False:
			t = time.struct_time((2021, 9, 19, 11, 43, 3, 0, -1, -1)) # off by +56 seconds after 5 days (+129.6 ppm)
			info("setting time to " + str(t))
			rtc.datetime = t
			t = rtc.datetime
			info("%04d-%02d-%02d" % (t.tm_year, t.tm_mon, t.tm_mday))
		#return rtc.i2c_device.device_address
		return 0x68
	except:
		warning("unable to set up RTC")
		raise

def get_timestring1():
	t = rtc.datetime
	return "%04d-%02d-%02d+%02d:%02d:%02d" % (t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec)

def get_timestring2():
	t = rtc.datetime
	return "%04d-%02d-%02d.%02d%02d%02d" % (t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec)

def get_timestring3():
	# https://en.wikipedia.org/wiki/ISO_8601
	t = rtc.datetime
	#info(str(t))
	#u = time.mktime(t)
	#info(str(u))
	#v = time.localtime(u)
	#info(str(v))
	return "%04d-%02d-%02dT%02d:%02d:%02d" % (t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec)

def set_from_timestruct(time):
	info("setting time to " + str(time))
	try:
		rtc.datetime = time
	except:
		warning("couldn't set RTC time")

