# last updated 2021-09-12 by mza

import time
import adafruit_pcf8523
from DebugInfoWarningError24 import debug, info, warning, error, debug2, debug3, set_verbosity, create_new_logfile_with_string_embedded, flush

def setup(i2c):
	global rtc
	try:
		rtc = adafruit_pcf8523.PCF8523(i2c)
		#info(get_timestring1())
		if False:
			t = time.struct_time((2021, 9, 12, 11, 31, 3, 0, -1, -1))
			info("setting time to " + str(t))
			rtc.datetime = t
			t = rtc.datetime
			info("%04d-%02d-%02d" % (t.tm_year, t.tm_mon, t.tm_mday))
	except:
		error("unable to set up RTC")
		return False
	return True

def get_timestring1():
	t = rtc.datetime
	return "%04d-%02d-%02d+%02d:%02d:%02d" % (t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec)

def get_timestring2():
	t = rtc.datetime
	return "%04d-%02d-%02d.%02d%02d%02d" % (t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec)

