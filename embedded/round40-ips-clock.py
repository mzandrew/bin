#!/usr/bin/env python3

# written 2024-01-18 by mza
# based on https://learn.adafruit.com/simplifying-qualia-cirtcuitpython-projects/usage
# and https://learn.adafruit.com/pico-w-wifi-with-circuitpython/pico-w-basic-wifi-test
# and https://docs.circuitpython.org/projects/ntp/en/latest/examples.html#set-rtc
# last updated 2024-01-24 by mza

# configuration:
length_of_hour_hand = 200
length_of_minute_hand = 300
distance_of_dot_from_center = 342
radius_of_dot = 10
background_color = 0x000000
color_of_hour_hand = 0x4444ff
color_of_minute_hand = 0xff0000
color_of_dot = 0x888888
width_of_hour_hand = 24
width_of_minute_hand = 16

# to install:
# rsync -a adafruit_qualia adafruit_portalbase adafruit_bitmap_font adafruit_display_text adafruit_io adafruit_minimqtt adafruit_display_shapes adafruit_requests.mpy adafruit_fakerequests.mpy adafruit_pca9554.mpy adafruit_focaltouch.mpy adafruit_cst8xx.mpy adafruit_miniqr.mpy adafruit_ntp.mpy /media/mza/CIRCUITPY/lib/

# to edit files with web workflow, you must disable usb mass storage (must be done in boot.py):
#import storage
#storage.disable_usb_drive()

import gc
import array
import time
import math
import wifi
import socketpool
import adafruit_ntp
import rtc
import displayio
from adafruit_qualia.graphics import Graphics, Displays # helps find the name "Displays.ROUND40"
from adafruit_display_shapes.line import Line
from adafruit_display_shapes.circle import Circle
from adafruit_display_shapes.polygon import Polygon
from adafruit_qualia.peripherals import Peripherals
import bitmaptools

#peripherals = Peripherals()
#peripherals.backlight = True
fake_the_network_being_down_counter = 0
#mode = "bitmaptools"
mode = "display_shapes"

# shows QR code for a URL:
if 0:
	webpage = "https://mzandrew.wordpress.com/"
	base = Graphics(Displays.ROUND40, default_bg=0x000000)
	peripherals = Peripherals(i2c_bus=base.i2c_bus)
	display = base.display
	qr_size = 9 # pixels
	scale = 15
	base.qrcode(
		webpage,
		qr_size=scale,
		x=(display.width // 2) - ((qr_size + 5) * scale),
		y=(display.height // 2) - ((qr_size + 4) * scale),
	)
	while True:
		if peripherals.button_up:
			peripherals.backlight = True
		if peripherals.button_down:
			peripherals.backlight = False
		time.sleep(0.1)

# tests basic internet connectivity:
if 0:
	import ipaddress
	wifi.radio.connect(os.getenv('CIRCUITPY_WIFI_SSID'), os.getenv('CIRCUITPY_WIFI_PASSWORD'))
	print("My MAC addr:", [hex(i) for i in wifi.radio.mac_address])
	print("My IP address is", wifi.radio.ipv4_address)
	ipv4 = ipaddress.ip_address("8.8.4.4")
	print("Ping google.com: %f ms" % (wifi.radio.ping(ipv4)*1000))

def dec(number, width=1, pad_with_zeroes=True):
	if pad_with_zeroes:
		return "%0*d" % (width, number)
	else:
		return "%*d" % (width, number)

def get_ntp_time_and_set_RTC():
	datetime = rtc.RTC().datetime
	print("rtc: " + str(datetime))
	try:
		global fake_the_network_being_down_counter
		if 0<fake_the_network_being_down_counter:
			fake_the_network_being_down_counter -= 1
			raise
		pool = socketpool.SocketPool(wifi.radio)
		ntp = adafruit_ntp.NTP(pool, tz_offset=-10)
		datetime = ntp.datetime
		print("ntp: " + str(datetime))
		rtc.RTC().datetime = datetime
		datetime = rtc.RTC().datetime
		print("rtc: " + str(datetime))
		global we_still_need_to_get_ntp_time; we_still_need_to_get_ntp_time = False
	except:
		print("can't get ntp time!")

def get_ntp_time_if_necessary():
	global we_still_need_to_get_ntp_time; we_still_need_to_get_ntp_time = False
	datetime = rtc.RTC().datetime
	if datetime.tm_year<2024:
		we_still_need_to_get_ntp_time = True
		get_ntp_time_and_set_RTC()
	else:
		print("rtc: " + str(datetime))

def convert_24bit_to_16bit(value_24bit):
	value_16bit = ((value_24bit>>19)&0x1f)<<11 | ((value_24bit>>10)&0x3f)<<5 | (value_24bit>>3)&0x1f
	#print(hex(value_24bit) + " -> " + hex(value_16bit))
	return value_16bit

def clear_bitmap():
	bitmaptools.fill_region(bitmap, 0, 0, graphics.display.width, graphics.display.height, convert_24bit_to_16bit(background_color))

def draw_clockface():
	print("draw_clockface()")
	if "bitmaptools"==mode:
		clear_bitmap()
	#objects = []
	for alpha in range(0, 60, 5):
		theta = twopi*alpha/60
		x0 = center_x + int(distance_of_dot_from_center*math.sin(theta))
		y0 = center_y - int(distance_of_dot_from_center*math.cos(theta))
		bonus=1.0
		if 0==alpha%15:
			bonus=1.5
		if "bitmaptools"==mode:
			bitmaptools.draw_circle(bitmap, x0, y0, int(bonus*radius_of_dot), convert_24bit_to_16bit(color_of_dot))
			bitmaptools.boundary_fill(bitmap, x0, y0, convert_24bit_to_16bit(color_of_dot), convert_24bit_to_16bit(background_color))
		else:
			object = Circle(x0=x0, y0=y0, r=int(bonus*radius_of_dot), fill=color_of_dot)
			graphics.display.root_group.append(object)
	#return objects

def setup():
	print()
	#convert_24bit_to_16bit(0xff0000)
	#convert_24bit_to_16bit(0x00ff00)
	#convert_24bit_to_16bit(0x0000ff)
	#global startup_time; startup_time = time.monotonic()
	global twopi; twopi = 2 * math.pi
	global graphics, bitmap
	graphics = Graphics(Displays.ROUND40, default_bg=None, auto_refresh=False)
	global center_x, center_y
	center_x = (graphics.display.width + 1) // 2
	center_y = (graphics.display.height + 1) // 2
	bitmap = displayio.Bitmap(graphics.display.width, graphics.display.height, 65535)
	tile_grid = displayio.TileGrid(bitmap, pixel_shader=displayio.ColorConverter(input_colorspace=displayio.Colorspace.RGB565))
	graphics.splash.append(tile_grid)
	graphics.display.root_group = graphics.splash
	get_ntp_time_if_necessary()
	draw_clockface()
	#diff = time.monotonic() - startup_time; print (str(diff))

def thickline(x1, y1, angle, length, width, color1, color2=background_color):
	x2 = x1 + int(length*math.sin(angle))
	y2 = y1 - int(length*math.cos(angle))
	#return Line(x1, y1, x2, y2, color1)
	#return Polygon(points=[(x1, y1), (x2, y2)], outline=color1)
	x_adjustment = int(width//2*math.cos(angle))
	y_adjustment = int(width//2*math.sin(angle))
	x3 = x1 + x_adjustment
	y3 = y1 + y_adjustment
	x4 = x1 + x_adjustment + int(length*math.sin(angle))
	y4 = y1 + y_adjustment - int(length*math.cos(angle))
	x5 = x1 - x_adjustment + int(length*math.sin(angle))
	y5 = y1 - y_adjustment - int(length*math.cos(angle))
	x6 = x1 - x_adjustment
	y6 = y1 - y_adjustment
	#print(str((x1, y1)) + " " + str((x2, y2)) + " " + str(points))
	if "bitmaptools"==mode:
		xs = array.array("i", (x3, x4, x5, x6))
		ys = array.array("i", (y3, y4, y5, y6))
		bitmaptools.draw_polygon(bitmap, xs, ys, convert_24bit_to_16bit(color1), 2)
		bitmaptools.boundary_fill(bitmap, (x2+x1)//2, (y2+y1)//2, convert_24bit_to_16bit(color1), convert_24bit_to_16bit(color2))
	else:
		points = []
		points.append((x3, y3))
		points.append((x4, y4))
		points.append((x5, y5))
		points.append((x6, y6))
		object = Polygon(points=points, outline=color1)
		graphics.display.root_group.append(object)
		return object

def draw_hour_and_minute_hands(hour, minute):
	minute_angle = twopi*minute/60
	hour_angle = twopi*hour12/12
	hour_angle += minute_angle/12
	minute_hand = thickline(center_x, center_y, minute_angle, length_of_minute_hand, width_of_minute_hand, color_of_minute_hand)
	hour_hand = thickline(center_x, center_y, hour_angle, length_of_hour_hand, width_of_hour_hand, color_of_hour_hand)
	#radius_of_middle_dot = max(width_of_minute_hand, width_of_hour_hand)//2 + 1
	#bitmaptools.draw_circle(bitmap, center_x, center_y, radius_of_middle_dot, convert_24bit_to_16bit(color_of_dot))
	#bitmaptools.boundary_fill(bitmap, center_x+2, center_y+2, convert_24bit_to_16bit(color_of_dot), convert_24bit_to_16bit(background_color))
	graphics.display.refresh()
	if "bitmaptools"==mode:
		thickline(center_x, center_y, minute_angle, length_of_minute_hand, width_of_minute_hand, background_color, color_of_minute_hand)
		thickline(center_x, center_y, hour_angle, length_of_hour_hand, width_of_hour_hand, background_color, color_of_hour_hand)
	else:
		graphics.display.root_group.remove(hour_hand)
		graphics.display.root_group.remove(minute_hand)
	#diff = time.monotonic() - startup_time; print (str(diff))

setup()
while True:
	datetime = rtc.RTC().datetime
	hour24 = datetime.tm_hour
	minute = datetime.tm_min
	second = datetime.tm_sec
	hour12 = hour24 % 12
	print(dec(hour24, 2) + ":" + dec(minute, 2) + ":" + dec(second, 2))
	if 0==minute:
		if "bitmaptools"==mode:
			draw_clockface()
	draw_hour_and_minute_hands(hour12, minute)
	if hour24==23 and minute==59:
		we_still_need_to_get_ntp_time = True
	if we_still_need_to_get_ntp_time:
		get_ntp_time_and_set_RTC()
	gc.collect() ; print(gc.mem_free())
	time.sleep(60 - rtc.RTC().datetime.tm_sec)

