# from pcf8523_adafruit.py
# last updated 2023-10-18 by mza

import time
import adafruit_ds3231
from DebugInfoWarningError24 import debug, info, warning, error, debug2, debug3, set_verbosity, create_new_logfile_with_string_embedded, flush, exception

def setup(i2c):
	global rtc
	try:
		rtc = adafruit_ds3231.DS3231(i2c)
		rtc.calibration = -30 # -30 * 4.34 ppm (to compensate for +130 ppm error)
		#info(get_timestring1())
		if False:
			t = time.struct_time((2022, 9, 14, 13, 20, 3, 0, -1, -1))
			info("setting time to " + str(t))
			rtc.datetime = t
			t = rtc.datetime
			info("%04d-%02d-%02d" % (t.tm_year, t.tm_mon, t.tm_mday))
		#return rtc.i2c_device.device_address
		return 0x68
	except (KeyboardInterrupt, ReloadException):
		raise
	except:
		warning("unable to set up RTC")
		raise

def get_timestring1():
	t = rtc.datetime
	return "%04d-%02d-%02d+%02d:%02d:%02d" % (t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec)

def get_timestring2(number_of_tries_remaining=3):
	if 0==number_of_tries_remaining:
		#return ""
		return "2000-01-01.000000"
	try:
		t = rtc.datetime
		return "%04d-%02d-%02d.%02d%02d%02d" % (t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec)
	except (KeyboardInterrupt, ReloadException):
		raise
	except Exception as e:
		exception(e)
		return get_timestring2(number_of_tries_remaining-1)

def set_from_timestruct(time, number_of_tries_remaining=3):
	#info("setting time to " + str(time))
	if 0==number_of_tries_remaining:
		return False
	try:
		rtc.datetime = time
		return True
	except (KeyboardInterrupt, ReloadException):
		raise
	except Exception as e:
		exception(e)
		return set_from_timestruct(time, number_of_tries_remaining-1)

