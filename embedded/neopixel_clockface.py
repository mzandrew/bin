# written 2022-10-29 by mza
# with help from https://learn.adafruit.com/adafruit-circuit-playground-express/circuitpython-neopixel
# and from https://learn.adafruit.com/adafruit-circuit-playground-express/circuitpython-digital-in-out
# and from https://learn.adafruit.com/circuitpython-essentials/circuitpython-neopixel
# last updated 2022-11-10 by mza

# cd lib
# rsync -r adafruit_ds3231.mpy adafruit_as7341.mpy adafruit_register /media/mza/CIRCUITPY/lib/
# cd ..
# rsync -av *.py /media/mza/CIRCUITPY/
# cp -a neopixel_clockface.py /media/mza/CIRCUITPY/code.py; sync

import time
import re
import board
import busio
import neopixel
import as7341_adafruit
import ds3231_adafruit
from DebugInfoWarningError24 import debug, info, warning, error, debug2, debug3, set_verbosity, create_new_logfile_with_string_embedded, flush

NEOPIXEL_BRIGHTNESS_MIN = 1
AMBIENT_BRIGHTNESS_FOR_MIN_NEOPIXEL_BRIGHTNESS = 1.0
NEOPIXEL_BRIGHTNESS_MAX = 6
AMBIENT_BRIGHTNESS_FOR_MAX_NEOPIXEL_BRIGHTNESS = 10.0
AMBIENT_CHANNEL = 5

NUMBER_OF_MINUTE_PIXELS = 60
NUMBER_OF_HOUR_PIXELS = 12
#NUMBER_OF_HOUR_PIXELS = 24

BLACK      = ( 0,  0,  0, 0)
WHITE      = ( 0,  0,  0, 1)
GREEN      = ( 0, 20,  0, 0)
BLUE       = ( 0,  0, 10, 0)
RED        = (10,  0,  0, 0)
DOT_HOUR   = ( 1,  1,  1, 0)
DOT_MINUTE = ( 1,  1,  1, 0)
minute_color = RED
hour_color = BLUE

N = 15 # average this many sensor readings before acting on it

if "adafruit_qtpy_esp32s2"==board.board_id:
	hours_neopixel_pin = board.A0
	minutes_neopixel_pin = board.A1
else: # kb2040
	hours_neopixel_pin = board.A3
	minutes_neopixel_pin = board.D2

def setup():
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
	global as7341_is_available
	as7341_is_available = False
	try:
		i2c_address = as7341_adafruit.setup(i2c, N)
		as7341_is_available = True
	except:
		warning("as7341 not found")
	global RTC_is_available
	RTC_is_available = False
	try:
		#i2c_address = pcf8523_adafruit.setup(i2c)
		i2c_address = ds3231_adafruit.setup(i2c)
		RTC_is_available = True
	except (KeyboardInterrupt, ReloadException):
		raise
	except:
		RTC_is_available = False
	setup_neopixel_clockface()

def setup_neopixel_clockface():
	global hours
	global minutes
	global brightness
	brightness = NEOPIXEL_BRIGHTNESS_MIN
	#brightness = NEOPIXEL_BRIGHTNESS_MAX
	hours = neopixel.NeoPixel(hours_neopixel_pin, NUMBER_OF_HOUR_PIXELS, pixel_order=(1, 0, 2, 3), brightness=1.0, auto_write=False)
	minutes = neopixel.NeoPixel(minutes_neopixel_pin, NUMBER_OF_MINUTE_PIXELS, pixel_order=(1, 0, 2, 3), brightness=1.0, auto_write=False)

def check_ambient_brightness():
	global n
	try:
		n
	except:
		n = 0
	as7341_adafruit.get_values()
	if as7341_is_available and N<=n:
		global brightness
		values = as7341_adafruit.get_average_values()
		info("ch[" + str(AMBIENT_CHANNEL) + "] = " + str(values[AMBIENT_CHANNEL]))
		if values[AMBIENT_CHANNEL]<AMBIENT_BRIGHTNESS_FOR_MIN_NEOPIXEL_BRIGHTNESS:
			brightness = NEOPIXEL_BRIGHTNESS_MIN
		elif AMBIENT_BRIGHTNESS_FOR_MAX_NEOPIXEL_BRIGHTNESS<values[AMBIENT_CHANNEL]:
			brightness = NEOPIXEL_BRIGHTNESS_MAX
		else:
			brightness = NEOPIXEL_BRIGHTNESS_MIN + (NEOPIXEL_BRIGHTNESS_MAX-NEOPIXEL_BRIGHTNESS_MIN)*(values[AMBIENT_CHANNEL]-AMBIENT_BRIGHTNESS_FOR_MIN_NEOPIXEL_BRIGHTNESS)/(AMBIENT_BRIGHTNESS_FOR_MAX_NEOPIXEL_BRIGHTNESS-AMBIENT_BRIGHTNESS_FOR_MIN_NEOPIXEL_BRIGHTNESS)
		info("new brightness = " + str(brightness))
		n = 0
	n += 1

def draw_clockface():
	info("updating clockface...")
	hours.fill(list(map(lambda x: int(x*brightness), BLACK)))
	for hh in range(0, NUMBER_OF_HOUR_PIXELS, NUMBER_OF_HOUR_PIXELS//4):
		hours[hh] = list(map(lambda x: int(x*brightness), DOT_HOUR))
	hours[h] = list(map(lambda x: int(x*brightness), hour_color))
	minutes.fill(list(map(lambda x: int(x*brightness), BLACK)))
	for mm in range(0, NUMBER_OF_MINUTE_PIXELS, NUMBER_OF_MINUTE_PIXELS//12):
		minutes[mm] = list(map(lambda x: int(x*brightness), DOT_MINUTE))
	minutes[m] = list(map(lambda x: int(x*brightness), minute_color))
	hours.show()
	minutes.show()

def parse_RTC():
	global h
	global m
	global old_minute
	global should_update_clockface
	if RTC_is_available:
		string = ds3231_adafruit.get_timestring2()
		info(string)
		match = re.search("[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]\.([0-9][0-9])([0-9][0-9])([0-9][0-9])", string)
		if match:
			h = match.group(1)
			m = match.group(2)
			s = match.group(3)
			h = int(h)
			m = int(m)
			s = int(s)
			h = h % 12
			#if 0==s:
			if not old_minute==m:
				should_update_clockface = True
				#info("hour = " + str(h))
				#info("minute = " + str(m))
				#info("second = " + str(s))
			old_minute = m

def loop():
	check_ambient_brightness()
	parse_RTC()
	global should_update_clockface
	if should_update_clockface:
		draw_clockface()
		should_update_clockface = False
	time.sleep(1)

if __name__ == "__main__":
	setup()
	h = 0
	m = 0
	old_minute = 0
	should_update_clockface = True
	while True:
		loop()

