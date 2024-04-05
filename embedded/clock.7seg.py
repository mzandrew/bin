#!/usr/bin/env python3

# written 2023-10-05 by mza
# borrowed bits and bobs from neopixel_clockface.py
# last updated 2023-10-18 by mza

# to install:
# cp -ar adafruit_register adafruit_ds3231.mpy adafruit_requests.mpy adafruit_io adafruit_minimqtt adafruit_display_text adafruit_ht16k33 /media/mza/7SEGCLOK/lib/
# cp -a ds3231_adafruit.py secrets.py airlift.py boxcar.py generic display_adafruit.py DebugInfoWarningError24.py /media/mza/7SEGCLOK/
# cp -a 7seg_clock.py /media/mza/7SEGCLOK/code.py; sync

import time
import re
import board
import busio
import display_adafruit
import ds3231_adafruit
import airlift
from generic import *
from DebugInfoWarningError24 import debug, info, warning, error, debug2, debug3, set_verbosity, create_new_logfile_with_string_embedded, flush, exception

my_wifi_name = "7segclock"

def connect_to_wifi_if_necessary_and_get_ntp_time():
	global airlift_is_available
	if not airlift_is_available:
		airlift_is_available = airlift.setup_wifi(my_wifi_name)
	if airlift_is_available:
		airlift.update_time_from_server()
		return True
	return False

def parse_RTC():
	# "2000-01-01.001146"
	global h12
	global h24
	global m
	global old_hour
	global old_minute
	global should_update_clockface
	global should_check_network_time
	global time_string
	if RTC_is_available:
		try:
			string = ds3231_adafruit.get_timestring2()
		except (KeyboardInterrupt, ReloadException):
			raise
		except Exception as e:
			exception(e)
			return
		debug(string)
		match = re.search("([0-9][0-9][0-9][0-9])-([0-9][0-9])-([0-9][0-9])\.([0-9][0-9])([0-9][0-9])([0-9][0-9])", string)
		if match:
			yyyy = int(match.group(1))
			mm = int(match.group(2))
			dd = int(match.group(3))
			h24 = match.group(4)
			m = match.group(5)
			s = match.group(6)
			h24 = int(h24)
			h12 = h24 % 12
			m = int(m)
			s = int(s)
			hms = str(h12) + ":" + "%0*d"%(2,m) + ":" + "%0*d"%(2,s)
			if 0==h12:
				time_string = dec(12, 2, False) + ":" + dec(m, 2, True)
			else:
				time_string = dec(h12, 2, False) + ":" + dec(m, 2, True)
			if not old_hour==h24:
				info(string + " " + hms)
				if 0==h24:
					should_check_network_time = True
					debug("just past midnight - need to update RTC from network time")
#			if not old_minute==m:
#				if 0==m%10:
#					should_check_network_time = True
			old_hour = h24
			if not old_minute==m:
				should_update_clockface = True
				debug("hour = " + str(h12))
				debug("minute = " + str(m))
				debug("second = " + str(s))
			old_minute = m
			if 2000==yyyy and 1==mm:
				debug("need to update RTC from network time")
				if connect_to_wifi_if_necessary_and_get_ntp_time():
					parse_RTC()

def setup():
	global old_hour
	global old_minute
	old_hour = 25
	old_minute = 61
	global time_string
	time_string = "12:00"
	global i2c
	try:
		i2c = busio.I2C(board.SCL1, board.SDA1)
		string = "using I2C1 "
	except (KeyboardInterrupt, ReloadException):
		raise
	except Exception as e:
		exception(e)
		#i2c = busio.I2C(board.SCL, board.SDA)
		i2c = board.I2C()
		string = "using I2C0 "
	info(string)
	global RTC_is_available
	RTC_is_available = False
	try:
		#i2c_address = pcf8523_adafruit.setup(i2c)
		i2c_address = ds3231_adafruit.setup(i2c)
		RTC_is_available = True
	except (KeyboardInterrupt, ReloadException):
		raise
	except Exception as e:
		exception(e)
		RTC_is_available = False
	if RTC_is_available:
		string = ds3231_adafruit.get_timestring2()
		info(string)
	else:
		info("RTC is not available")
	display_adafruit.setup_7seg_numeric_backpack_4(i2c)
	global airlift_is_available
	airlift_is_available = False
	if 0:
		connect_to_wifi_if_necessary_and_get_ntp_time()

def loop():
	global should_check_network_time
	if should_check_network_time:
		if connect_to_wifi_if_necessary_and_get_ntp_time():
			should_check_network_time = False
	parse_RTC()
	global should_update_clockface
	if should_update_clockface:
		info(time_string)
		try:
			display_adafruit.update_string_on_7seg_numeric_backpack_4(time_string)
			should_update_clockface = False
		except (KeyboardInterrupt, ReloadException):
			raise
		except Exception as e:
			exception(e)
			pass
	time.sleep(1)

if __name__ == "__main__":
	setup()
	should_update_clockface = True
	should_check_network_time = False
	while True:
		loop()

