#!/usr/bin/env python3

# written 2024-01-18 by mza
# based on https://learn.adafruit.com/simplifying-qualia-cirtcuitpython-projects/usage
# and https://learn.adafruit.com/pico-w-wifi-with-circuitpython/pico-w-basic-wifi-test
# and https://docs.circuitpython.org/projects/ntp/en/latest/examples.html#set-rtc
# last updated 2024-01-18 by mza

# configuration:
length_of_hour_hand = 200
length_of_minute_hand = 300
distance_of_dot_from_center = 345
radius_of_dot = 10
background_color = 0x000000
color_of_hour_hand = 0x4444ff
color_of_minute_hand = 0xff0000
color_of_dot = 0x666666
width_of_hour_hand = 24
width_of_minute_hand = 16

# to install:
# rsync -a adafruit_qualia adafruit_portalbase adafruit_bitmap_font adafruit_display_text adafruit_io adafruit_minimqtt adafruit_display_shapes adafruit_requests.mpy adafruit_fakerequests.mpy adafruit_pca9554.mpy adafruit_focaltouch.mpy adafruit_cst8xx.mpy adafruit_miniqr.mpy adafruit_ntp.mpy /media/mza/CIRCUITPY/lib/

# to edit files with web workflow, you must disable usb mass storage (must be done in boot.py):
#import storage
#storage.disable_usb_drive()

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

#peripherals = Peripherals()
#peripherals.backlight = True
fake_the_network_being_down_counter = 0

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

def draw_clockface():
	for alpha in range(0, 60, 5):
		theta = twopi*alpha/60
		x0 = center_x + int(distance_of_dot_from_center*math.sin(theta))
		y0 = center_y - int(distance_of_dot_from_center*math.cos(theta))
		graphics.display.root_group.append(Circle(x0=x0, y0=y0, r=radius_of_dot, fill=color_of_dot))

def setup():
	print()
	#global startup_time; startup_time = time.monotonic()
	global graphics, bitmap
	graphics = Graphics(Displays.ROUND40, default_bg=None, auto_refresh=False)
	bitmap = displayio.Bitmap(graphics.display.width, graphics.display.height, 65535)
	tile_grid = displayio.TileGrid(bitmap, pixel_shader=displayio.ColorConverter(input_colorspace=displayio.Colorspace.RGB565))
	graphics.splash.append(tile_grid)
	graphics.display.root_group = graphics.splash
	global center_x, center_y
	center_x = (graphics.display.width + 1) // 2
	center_y = (graphics.display.height + 1) // 2
	global twopi; twopi = 2 * math.pi
	get_ntp_time_if_necessary()
	draw_clockface()
	#diff = time.monotonic() - startup_time; print (str(diff))

def thickline(x1, y1, angle, length, width, color):
	#x2 = x1 + int(length*math.sin(angle))
	#y2 = y1 - int(length*math.cos(angle))
	#return Line(x1, y1, x2, y2, color)
	#return Polygon(points=[(x1, y1), (x2, y2)], outline=color)
	points = []
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
	points.append((x3, y3))
	points.append((x4, y4))
	points.append((x5, y5))
	points.append((x6, y6))
	#print(str((x1, y1)) + " " + str((x2, y2)) + " " + str(points))
	return Polygon(points=points, outline=color)

def draw_hour_and_minute_hands(hour, minute):
	minute_angle = twopi*minute/60
	hour_angle = twopi*hour12/12
	hour_angle += minute_angle/12
	graphics.display.root_group.append(thickline(center_x, center_y, minute_angle, length_of_minute_hand, width_of_minute_hand, color_of_minute_hand))
	graphics.display.root_group.append(thickline(center_x, center_y, hour_angle, length_of_hour_hand, width_of_hour_hand, color_of_hour_hand))
	radius_of_middle_dot = max(width_of_minute_hand, width_of_hour_hand)//2 + 1
	graphics.display.root_group.append(Circle(x0=center_x, y0=center_y, r=radius_of_middle_dot, fill=color_of_dot))
	graphics.display.refresh()
	graphics.display.root_group.append(thickline(center_x, center_y, minute_angle, length_of_minute_hand, width_of_minute_hand, background_color))
	graphics.display.root_group.append(thickline(center_x, center_y, hour_angle, length_of_hour_hand, width_of_hour_hand, background_color))
	#diff = time.monotonic() - startup_time; print (str(diff))

setup()
while True:
	datetime = rtc.RTC().datetime
	hour24 = datetime.tm_hour
	minute = datetime.tm_min
	second = datetime.tm_sec
	hour12 = hour24 % 12
	print(dec(hour24, 2) + ":" + dec(minute, 2) + ":" + dec(second, 2))
	draw_hour_and_minute_hands(hour12, minute)
	if hour24==23 and minute==59:
		we_still_need_to_get_ntp_time = True
	if we_still_need_to_get_ntp_time:
		get_ntp_time_and_set_RTC()
	time.sleep(60 - rtc.RTC().datetime.tm_sec)

