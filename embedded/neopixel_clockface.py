# written 2022-10-29 by mza
# with help from https://learn.adafruit.com/adafruit-circuit-playground-express/circuitpython-neopixel
# and from https://learn.adafruit.com/adafruit-circuit-playground-express/circuitpython-digital-in-out
# and from https://learn.adafruit.com/circuitpython-essentials/circuitpython-neopixel
# last updated 2024-01-16 by mza

# to install:
# cd lib
# rsync -r adafruit_ds3231.mpy adafruit_as7341.mpy neopixel.mpy adafruit_minimqtt simpleio.mpy adafruit_esp32spi adafruit_register adafruit_io adafruit_requests.mpy adafruit_bus_device /media/mza/CIRCUITPY/lib/
# cd ..
# rsync -av *.py /media/mza/CIRCUITPY/
# cp -a neopixel_clockface.py /media/mza/CIRCUITPY/code.py; sync

import time
import re
import math
import board
import busio
import neopixel
import as7341_adafruit
import ds3231_adafruit
import airlift
from DebugInfoWarningError24 import debug, info, warning, error, debug2, debug3, set_verbosity, create_new_logfile_with_string_embedded, flush

NEOPIXEL_BRIGHTNESS_MIN = 1.0
AMBIENT_BRIGHTNESS_FOR_MIN_NEOPIXEL_BRIGHTNESS = 0.0
NEOPIXEL_BRIGHTNESS_MAX = 6.0
AMBIENT_BRIGHTNESS_FOR_MAX_NEOPIXEL_BRIGHTNESS = 2.0

mode = "normal"
#mode = "pulsed"
PULSE_TIMING_ON_ms = 1000

AMBIENT_CHANNEL = 5
NUMBER_OF_MINUTE_PIXELS = 60
OFFSET_FOR_MINUTE_HAND = 7
NUMBER_OF_PIXELS_PER_HOUR = 8 # 1=ring_of_12; 2=ring_of_24; 8=12_sticks
FIRST_PIXEL_TO_LIGHT_UP_FOR_HOUR = 7 # 0=ring_of_12; 0,1=ring_of_24; [0-7]=12_sticks
NUMBER_OF_PIXELS_TO_LIGHT_UP_PER_HOUR = 1 # 1=ring_of_12; 1,2=ring_of_24; [1-8]=12_sticks
FIRST_PIXEL_TO_LIGHT_UP_FOR_HOUR_DOT = 6 # 0=ring_of_12; 0,1=ring_of_24; [0-7]=12_sticks
NUMBER_OF_PIXELS_TO_LIGHT_UP_PER_HOUR_DOT = 2 # 1=ring_of_12; 1,2=ring_of_24; [1-8]=12_sticks
NUMBER_OF_HOUR_PIXELS = 12*NUMBER_OF_PIXELS_PER_HOUR

USE_TRUE_WHITE = False # use special white led or light up red, green and blue [note: the sticks do not have true white]
ILLUMINATE_EVERY_THREE_HOURS = False # 12, 3, 6, 9
ILLUMINATE_EVERY_FIVE_MINUTES = False # 0, 5, 10, ..., 55
ILLUMINATE_EVERY_FIFTEEN_MINUTES = False # 0, 15, 30, 45

BLACK           = ( 0,  0,  0, 0)
TRUE_WHITE      = ( 0,  0,  0, 1)
COMPOSITE_WHITE = ( 1,  1,  1, 0)
GREEN           = ( 0,  1,  0, 0)
BLUE            = ( 0,  0,  1, 0)
RED             = ( 1,  0,  0, 0)
if ILLUMINATE_EVERY_THREE_HOURS:
	if USE_TRUE_WHITE:
		DOT_HOUR   = TRUE_WHITE
	else:
		DOT_HOUR   = COMPOSITE_WHITE
else:
	DOT_HOUR   = BLACK
if ILLUMINATE_EVERY_FIVE_MINUTES:
	if USE_TRUE_WHITE:
		DOT_MINUTE_FIVE = TRUE_WHITE
	else:
		DOT_MINUTE_FIVE = COMPOSITE_WHITE
else:
	DOT_MINUTE_FIVE = BLACK
if ILLUMINATE_EVERY_FIFTEEN_MINUTES:
	if USE_TRUE_WHITE:
		DOT_MINUTE_FIFTEEN = TRUE_WHITE
	else:
		DOT_MINUTE_FIFTEEN = COMPOSITE_WHITE
else:
	DOT_MINUTE_FIFTEEN = BLACK
minute_color = RED
hour_color = BLUE

N = 15 # average this many sensor readings before acting on it
my_wifi_name = "neopixelclock"
eta = 1.0/512.0

if "adafruit_qtpy_esp32s2"==board.board_id:
	hours_neopixel_pin = board.A0
	minutes_neopixel_pin = board.A1
else: # kb2040
	hours_neopixel_pin = board.A3
	minutes_neopixel_pin = board.D2

def quantize_in_etas(value):
	#info(str(value))
	value *= 1.0/eta
	#info(str(value))
	value = int(value)
	#info(str(value))
	value *= eta
	#info(str(value))
	return value

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
	except (KeyboardInterrupt, ReloadException):
		raise
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
	global airlift_is_available
	airlift_is_available = False
	if RTC_is_available:
		string = ds3231_adafruit.get_timestring2()
		info("RTC: " + string)
		parse_RTC()
		if yyyy<2024:
			airlift_is_available = airlift.setup_wifi(my_wifi_name)
			debug("need to update RTC from network time")
			if airlift_is_available:
				airlift.update_time_from_server()
	else:
		airlift_is_available = airlift.setup_wifi(my_wifi_name)
		debug("need to update RTC from network time")
		if airlift_is_available:
			airlift.update_time_from_server()
	setup_neopixel_clockface()

def setup_neopixel_clockface():
	global hours
	global minutes
	global brightness
	brightness = NEOPIXEL_BRIGHTNESS_MIN
	if 8==NUMBER_OF_PIXELS_PER_HOUR:
		hours = neopixel.NeoPixel(hours_neopixel_pin, NUMBER_OF_HOUR_PIXELS, brightness=brightness, auto_write=False)
	else:
		hours = neopixel.NeoPixel(hours_neopixel_pin, NUMBER_OF_HOUR_PIXELS, pixel_order=(1, 0, 2, 3), brightness=brightness, auto_write=False)
	minutes = neopixel.NeoPixel(minutes_neopixel_pin, NUMBER_OF_MINUTE_PIXELS, pixel_order=(1, 0, 2, 3), brightness=brightness, auto_write=False)

def check_ambient_brightness():
	global n
	try:
		n
	except (KeyboardInterrupt, ReloadException):
		raise
	except:
		n = 0
	as7341_adafruit.get_values()
	if as7341_is_available and N<=n:
		global brightness
		global old_brightness
		global should_update_clockface
		values = as7341_adafruit.get_average_values()
		if values[AMBIENT_CHANNEL]<AMBIENT_BRIGHTNESS_FOR_MIN_NEOPIXEL_BRIGHTNESS:
			brightness = NEOPIXEL_BRIGHTNESS_MIN
		elif AMBIENT_BRIGHTNESS_FOR_MAX_NEOPIXEL_BRIGHTNESS<values[AMBIENT_CHANNEL]:
			brightness = NEOPIXEL_BRIGHTNESS_MAX
		else:
			brightness = NEOPIXEL_BRIGHTNESS_MIN + (NEOPIXEL_BRIGHTNESS_MAX-NEOPIXEL_BRIGHTNESS_MIN)*(values[AMBIENT_CHANNEL]-AMBIENT_BRIGHTNESS_FOR_MIN_NEOPIXEL_BRIGHTNESS)/(AMBIENT_BRIGHTNESS_FOR_MAX_NEOPIXEL_BRIGHTNESS-AMBIENT_BRIGHTNESS_FOR_MIN_NEOPIXEL_BRIGHTNESS)
		brightness = quantize_in_etas(brightness)
		global brightness_string
		brightness_string = "ambient light (ch[" + str(AMBIENT_CHANNEL) + "]) = " + str(values[AMBIENT_CHANNEL]) + "; new brightness = " + str(brightness)
		n = 0
		if eta<math.fabs(old_brightness-brightness):
			should_update_clockface = True
			debug("updating clockface due to ambient light conditions change")
		old_brightness = brightness
	n += 1

def draw_clockface():
	debug("updating clockface...")
	hours.fill(list(map(lambda x: int(x*brightness), BLACK)))
	for hh in range(0, 12, 3): # 0,3,6,9
		for i in range(FIRST_PIXEL_TO_LIGHT_UP_FOR_HOUR_DOT, FIRST_PIXEL_TO_LIGHT_UP_FOR_HOUR_DOT + NUMBER_OF_PIXELS_TO_LIGHT_UP_PER_HOUR_DOT): # [0] or [0,1] or [0,7]
			hours[hh*NUMBER_OF_PIXELS_PER_HOUR+i] = list(map(lambda x: int(x*brightness), DOT_HOUR)) # 0,3,... or 0,1,6,7,... or 0,1,2,3,4,5,6,7,24,25,26,27,28,29,30,31,...
	for i in range(FIRST_PIXEL_TO_LIGHT_UP_FOR_HOUR, FIRST_PIXEL_TO_LIGHT_UP_FOR_HOUR + NUMBER_OF_PIXELS_TO_LIGHT_UP_PER_HOUR): # [0] or [0,1] or [0,7]
		hours[h12*NUMBER_OF_PIXELS_PER_HOUR+i] = list(map(lambda x: int(x*brightness), hour_color))
	minutes.fill(list(map(lambda x: int(x*brightness), BLACK))) # [0,59]
	for mm in range(OFFSET_FOR_MINUTE_HAND, OFFSET_FOR_MINUTE_HAND+NUMBER_OF_MINUTE_PIXELS, NUMBER_OF_MINUTE_PIXELS//12): # [7,66]
		minutes[mm%NUMBER_OF_MINUTE_PIXELS] = list(map(lambda x: int(x*brightness), DOT_MINUTE_FIVE)) # [7,59],[0,6]
	for mm in range(OFFSET_FOR_MINUTE_HAND, OFFSET_FOR_MINUTE_HAND+NUMBER_OF_MINUTE_PIXELS, NUMBER_OF_MINUTE_PIXELS//4): # [7,66]
		minutes[mm%NUMBER_OF_MINUTE_PIXELS] = list(map(lambda x: int(x*brightness), DOT_MINUTE_FIFTEEN)) # [7,59],[0,6]
	minutes[(m+OFFSET_FOR_MINUTE_HAND)%NUMBER_OF_MINUTE_PIXELS] = list(map(lambda x: int(x*brightness), minute_color))
	minutes.show()
	hours.show()
	if mode=="pulsed":
		time.sleep(PULSE_TIMING_ON_ms/1000)
		hours.fill(list(map(lambda x: int(x*brightness), BLACK)))
		hours.show()

def parse_RTC():
	# "2000-01-01.001146"
	global h12
	global h24
	global m
	global yyyy
	global old_hour
	global old_minute
	global should_update_clockface
	global should_check_network_time
	if RTC_is_available:
		string = ds3231_adafruit.get_timestring2()
		debug2(string)
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
			if not old_hour==h24:
				info(string + " " + hms + " " + brightness_string)
				if 0==h24:
					should_check_network_time = True
					debug("just past midnight - need to update RTC from network time")
			else:
				debug(brightness_string)
			old_hour = h24
			if not old_minute==m:
				should_update_clockface = True
				debug("hour = " + str(h12) + " minute = " + str(m) + " second = " + str(s))
			old_minute = m
			if yyyy<2024:
				debug("need to update RTC from network time")
				global airlift_is_available
				if not airlift_is_available:
					airlift_is_available = airlift.setup_wifi(my_wifi_name)
				if airlift_is_available:
					airlift.update_time_from_server()
					parse_RTC()

def loop():
	global should_check_network_time
	if should_check_network_time:
		global airlift_is_available
		if not airlift_is_available:
			airlift_is_available = airlift.setup_wifi(my_wifi_name)
		if airlift_is_available:
			airlift.update_time_from_server()
		should_check_network_time = False
	check_ambient_brightness()
	parse_RTC()
	global should_update_clockface
	if should_update_clockface:
		draw_clockface()
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
	old_brightness = 0
	brightness_string = ""
	should_update_clockface = True
	should_check_network_time = False
	setup()
	info("")
	while True:
		loop()

