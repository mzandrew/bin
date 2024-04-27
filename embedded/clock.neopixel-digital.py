# written 2022-10-29 by mza
# based on neopixel_clockface.py
# with help from https://learn.adafruit.com/adafruit-circuit-playground-express/circuitpython-neopixel
# and from https://learn.adafruit.com/adafruit-circuit-playground-express/circuitpython-digital-in-out
# and from https://learn.adafruit.com/circuitpython-essentials/circuitpython-neopixel
# last updated 2024-04-27 by mza

# to install:
# cd lib
# rsync -r adafruit_ntp.mpy neopixel.mpy /media/mza/CIRCUITPY/lib/
# cd ..
# rsync -av DebugInfoWarningError24.py /media/mza/CIRCUITPY/
# cp -a clock.neopixel-digital.py /media/mza/CIRCUITPY/code.py; sync

import time
import re
import math
import board
import busio
import neopixel
#import ds3231_adafruit
import rtc
import adafruit_ntp
from DebugInfoWarningError24 import debug, info, warning, error, debug2, debug3, set_verbosity, create_new_logfile_with_string_embedded, flush

BLACK           = ( 0,  0,  0, 0)
TRUE_WHITE      = ( 0,  0,  0, 1)
COMPOSITE_WHITE = ( 1,  1,  1, 0)
GREEN           = ( 0,  1,  0, 0)
BLUE            = ( 0,  0,  1, 0)
RED             = ( 1,  0,  0, 0)
PURPLE          = ( 1,  0,  1, 0)

NUMBER_OF_PIXELS_PER_DIGIT = 32
brightness = 1.0

#if "adafruit_qtpy_esp32s3_4mbflash_2mbpsram"==board.board_id:

def get_ntp_time_and_set_RTC():
	datetime = rtc.RTC().datetime
	print("rtc: " + str(datetime))
	try:
		import wifi
		import socketpool
		pool = socketpool.SocketPool(wifi.radio)
		import adafruit_ntp
		ntp = adafruit_ntp.NTP(pool, tz_offset=-10)
		try:
			datetime = ntp.datetime # OSError: [Errno 116] ETIMEDOUT
		except:
			raise
		print("ntp: " + str(datetime))
		rtc.RTC().datetime = datetime
		datetime = rtc.RTC().datetime
		print("rtc: " + str(datetime))
		global we_still_need_to_get_ntp_time; we_still_need_to_get_ntp_time = False
	except:
		print("can't get ntp time!")
		#raise

def get_ntp_time_if_necessary():
	global we_still_need_to_get_ntp_time; we_still_need_to_get_ntp_time = False
	datetime = rtc.RTC().datetime
	if datetime.tm_year<2024:
		we_still_need_to_get_ntp_time = True
		get_ntp_time_and_set_RTC()
	else:
		print("rtc: " + str(datetime))

def parse_RTC():
	global h12
	global h24
	global m
	global yyyy
	global old_hour
	global old_minute
	global should_update_clockface
	global should_check_network_time
	datetime = rtc.RTC().datetime
	#print("rtc: " + str(datetime))
	yyyy = datetime.tm_year
	mm = datetime.tm_mon
	dd = datetime.tm_mday
	h24 = datetime.tm_hour
	m = datetime.tm_min
	s = datetime.tm_sec
	h12 = h24 % 12
	hms = str(h12) + ":" + "%0*d"%(2,m) + ":" + "%0*d"%(2,s)
	if not old_hour==h24:
		info(hms)
		if 0==h24:
			should_check_network_time = True
			debug("just past midnight - need to update RTC from network time")
	old_hour = h24
	if not old_minute==m:
		should_update_clockface = True
		debug("hour = " + str(h12) + " minute = " + str(m) + " second = " + str(s))
	old_minute = m
	if yyyy<2024:
		debug("need to update RTC from network time")
		should_check_network_time = True

def setup():
	print("")
	global RTC_is_available
	RTC_is_available = False
	if 0:
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
		try:
			#i2c_address = pcf8523_adafruit.setup(i2c)
			i2c_address = ds3231_adafruit.setup(i2c)
			RTC_is_available = True
		except (KeyboardInterrupt, ReloadException):
			raise
		except:
			RTC_is_available = False
	parse_RTC()
	if yyyy<2024:
		get_ntp_time_and_set_RTC()
	setup_neopixel_clockface()

font_4x8 = [ 0 for i in range(11) ]
font_4x8[0] = ( 0,0,1,1,1,1,1,0,
                0,1,0,0,0,0,0,1,
                0,1,0,0,0,0,0,1,
                0,0,1,1,1,1,1,0 )
font_4x8[1] = ( 0,0,0,0,0,0,0,0,
                0,1,1,1,1,1,1,1,
                0,0,0,0,0,0,0,0,
                0,0,0,0,0,0,0,0 )
font_4x8[2] = ( 0,0,1,1,0,0,0,1,
                0,1,0,0,1,0,0,1,
                0,1,0,0,1,0,0,1,
                0,0,1,0,0,1,1,1 )
font_4x8[3] = ( 0,0,1,1,1,1,1,0,
                0,1,0,0,1,0,0,1,
                0,1,0,0,1,0,0,1,
                0,1,0,0,0,0,0,1 )
font_4x8[4] = ( 0,1,1,1,1,1,1,1,
                0,0,0,0,1,0,0,0,
                0,0,0,0,1,0,0,0,
                0,1,1,1,1,0,0,0 )
font_4x8[5] = ( 0,1,0,0,0,1,1,0,
                0,1,0,0,1,0,0,1,
                0,1,0,0,1,0,0,1,
                0,1,1,1,1,0,1,0 )
font_4x8[6] = ( 0,0,0,0,0,1,1,0,
                0,1,0,0,1,0,0,1,
                0,1,0,0,1,0,0,1,
                0,0,1,1,1,1,1,0 )
#font_4x8[7] = ( 0,1,1,1,1,1,1,1,
#                0,1,0,0,0,0,0,0,
#                0,1,0,0,0,0,0,0,
#                0,1,0,0,0,0,0,0 )
font_4x8[7] = ( 0,1,1,1,0,0,0,0,
                0,1,0,0,1,1,0,0,
                0,1,0,0,0,0,1,1,
                0,1,0,0,0,0,0,0 )
font_4x8[8] = ( 0,0,1,1,0,1,1,0,
                0,1,0,0,1,0,0,1,
                0,1,0,0,1,0,0,1,
                0,0,1,1,0,1,1,0 )
font_4x8[9] = ( 0,0,1,1,1,1,1,0,
                0,1,0,0,1,0,0,1,
                0,1,0,0,1,0,0,1,
                0,0,1,1,0,0,0,0 )
font_4x8[10] = ( 0,0,0,0,0,0,0,0,
                 0,0,0,0,0,0,0,0,
                 0,0,0,0,0,0,0,0,
                 0,0,0,0,0,0,0,0 )

def setup_neopixel_clockface():
	global digit
	digit = []
	digit.append(neopixel.NeoPixel(board.A0, NUMBER_OF_PIXELS_PER_DIGIT, auto_write=False))
	digit.append(neopixel.NeoPixel(board.A1, NUMBER_OF_PIXELS_PER_DIGIT, auto_write=False))
	digit.append(neopixel.NeoPixel(board.A2, NUMBER_OF_PIXELS_PER_DIGIT, auto_write=False))
	digit.append(neopixel.NeoPixel(board.A3, NUMBER_OF_PIXELS_PER_DIGIT, auto_write=False))

def draw_digital_clockface():
	datetime = rtc.RTC().datetime
	for i in range(4):
		h24 = datetime.tm_hour
		h12 = h24 % 12
		m = datetime.tm_min
		if 3==i: # hh:mM
			k = m%10
		if 2==i: # hh:Mm
			k = m//10
		if 1==i: # hH:mm
			k = h12%10
		if 0==i: # Hh:mm
			k = h12//10
			if 0==k:
				k = 10
		digit[i].fill(list(map(lambda x: int(x*brightness), BLACK)))
		for j in range(NUMBER_OF_PIXELS_PER_DIGIT):
			digit[i][j] = list(map(lambda x: int(x*brightness*font_4x8[k][j]), PURPLE))
	for i in range(4):
		digit[i].show()

def loop():
	global should_check_network_time
	if should_check_network_time:
		should_check_network_time = False
		get_ntp_time_and_set_RTC()
	parse_RTC()
	global should_update_clockface
	if should_update_clockface:
		draw_digital_clockface()
		should_update_clockface = False
	time.sleep(1)

if __name__ == "__main__":
	set_verbosity(4)
	h12 = 0
	h24 = 0
	m = 0
	yyyy = 2000
	old_minute = 0
	old_hour = 0
	should_update_clockface = True
	should_check_network_time = False
	setup()
	info("")
	while True:
		loop()

