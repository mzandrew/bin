#!/usr/bin/env python3

# written 2024-01-18 by mza
# based on https://learn.adafruit.com/simplifying-qualia-cirtcuitpython-projects/usage
# and https://learn.adafruit.com/pico-w-wifi-with-circuitpython/pico-w-basic-wifi-test
# and https://docs.circuitpython.org/projects/ntp/en/latest/examples.html#set-rtc
# https://docs.circuitpython.org/projects/display-shapes/en/latest/api.html
# https://docs.circuitpython.org/en/latest/shared-bindings/bitmaptools/index.html
# last updated 2024-01-24 by mza

# to install:
# cd lib9
# rsync -a adafruit_qualia adafruit_portalbase adafruit_bitmap_font adafruit_display_text adafruit_io adafruit_minimqtt adafruit_display_shapes adafruit_requests.mpy adafruit_fakerequests.mpy adafruit_pca9554.mpy adafruit_focaltouch.mpy adafruit_cst8xx.mpy adafruit_miniqr.mpy adafruit_ntp.mpy /media/mza/CIRCUITPY/lib/
# cd ..
# cp -a settings.toml /media/mza/CIRCUITPY/
# cp -a round40-ips-clock.py /media/mza/CIRCUITPY/code.py; sync

# configuration:
length_of_hour_hand = 200
length_of_minute_hand = 300
distance_of_dot_from_center = 342
radius_of_dot = 10
width_of_hour_hand = 24
width_of_minute_hand = 16
subbitmap_width = 720
subbitmap_height = 720
subbitmap_center_x = subbitmap_width//2
subbitmap_center_y = subbitmap_height//2
FONTSCALE = 2
titles_offset_x = 150
titles_offset_y = -50
dates_offset_x = -200
dates_offset_y = -52
days_offset_x = -200
days_offset_y = 77
NUMBER_OF_CLOCKFACES = 1
worldclock_text = [ " " ]
offset_timezone = [ 0 ]
offset_x = [ 0 ]
offset_y = [ 0 ]

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
#from adafruit_qualia.peripherals import Peripherals
from adafruit_display_shapes.circle import Circle
from adafruit_display_shapes.polygon import Polygon
from adafruit_display_text import bitmap_label
from adafruit_datetime import _DAYNAMES
from terminalio import FONT
import bitmaptools

rotation_angle=0*math.pi/2
#palette_colors = 65535
palette_colors = 6
palette = displayio.Palette(palette_colors)
palette[0] = 0x000000 # black
palette[1] = 0xff0000 # red
palette[2] = 0x00ff00 # green
palette[3] = 0x4444ff # light blue
palette[4] = 0x999999 # grey
palette[5] = 0xffffff # white
background_color = 0
color_of_hour_hand = 3
color_of_minute_hand = 1
color_of_dot = 4

#peripherals = Peripherals()
#peripherals.backlight = True
fake_the_network_being_down_counter = 0
#mode = "bitmaptools"
#mode = "display_shapes"
mode = "rotozoom"

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
		raise

def get_ntp_time_if_necessary():
	global we_still_need_to_get_ntp_time; we_still_need_to_get_ntp_time = False
	datetime = rtc.RTC().datetime
	if datetime.tm_year<2024:
		we_still_need_to_get_ntp_time = True
		get_ntp_time_and_set_RTC()
	else:
		print("rtc: " + str(datetime))

def clear_bitmap(bitmap_name):
	bitmaptools.fill_region(bitmap_name, 0, 0, bitmap_name.width, bitmap_name.height, background_color)

def draw_clockface():
	print("draw_clockface()")
	if "bitmaptools"==mode:
		clear_bitmap(bitmap)
		clear_bitmap(dots_bitmap)
	#objects = []
	for alpha in range(0, 60, 5):
		theta = twopi*alpha/60
		x0 = subbitmap_center_x + int(distance_of_dot_from_center*math.sin(theta))
		y0 = subbitmap_center_y - int(distance_of_dot_from_center*math.cos(theta))
		bonus=1.0
		if 0==alpha%15:
			bonus=1.5
		if "display_shapes"==mode:
			object = Circle(x0=x0, y0=y0, r=int(bonus*radius_of_dot), fill=color_of_dot)
			display.root_group.append(object)
		else:
			bitmaptools.draw_circle(dots_bitmap, x0, y0, int(bonus*radius_of_dot), color_of_dot)
			bitmaptools.boundary_fill(dots_bitmap, x0, y0, color_of_dot, background_color)
	#return objects

def setup():
	print()
	#global startup_time; startup_time = time.monotonic()
	global twopi; twopi = 2 * math.pi
	global display, bitmap
	gc.collect(); print(gc.mem_free())
	if 1:
		#graphics = Graphics(Displays.BAR320X960, default_bg=None, auto_refresh=False)
		graphics = Graphics(Displays.ROUND40, default_bg=None, auto_refresh=False)
		display = graphics.display
		splash = graphics.splash
	else:
		displayio.release_displays()
		import board
		spi = board.SPI()
		if board.board_id=="adafruit_feather_esp32_v2":
			tft_cs = board.D15
			tft_dc = board.D33
		else:
			tft_cs = board.D9
			tft_dc = board.D10
		display_width = 480
		display_height = 320
		display_bus = displayio.FourWire(spi, command=tft_dc, chip_select=tft_cs)
		from adafruit_hx8357 import HX8357
		display = HX8357(display_bus, width=display_width, height=display_height)
		splash = displayio.Group()
		display.auto_refresh = False
	gc.collect(); print(gc.mem_free())
	bitmap = displayio.Bitmap(display.width, display.height, palette_colors)
	global center_x, center_y
	center_x = (display.width + 1) // 2
	center_y = (display.height + 1) // 2
	global dots_bitmap
	dots_bitmap = displayio.Bitmap(subbitmap_width, subbitmap_height, palette_colors)
	tile_grid = displayio.TileGrid(bitmap, pixel_shader=palette)
	splash.append(tile_grid)
	display.root_group = splash
	get_ntp_time_if_necessary()
	draw_clockface()
	global t_struct
	t_struct = [ 0 for i in range(NUMBER_OF_CLOCKFACES) ]
	update_t_struct()
	if "rotozoom"==mode:
		generate_worldclock_titles()
		global worldclock_dates
		worldclock_dates = [ 0 for i in range(NUMBER_OF_CLOCKFACES) ]
		global worldclock_days
		worldclock_days = [ 0 for i in range(NUMBER_OF_CLOCKFACES) ]
		update_worldclock_dates()
		update_worldclock_days_AMPM()
		generate_rotozoom_hands()
	#diff = time.monotonic() - startup_time; print (str(diff))

def update_t_struct():
	global t_struct
	datetime = rtc.RTC().datetime
	for i in range(NUMBER_OF_CLOCKFACES):
		t_struct[i] = time.localtime(time.mktime(datetime) + offset_timezone[i]*3600)

def generate_worldclock_titles():
	global worldclock_titles
	worldclock_titles = []
	for i in range(NUMBER_OF_CLOCKFACES):
		worldclock_titles.append(bitmap_label.Label(FONT, text=worldclock_text[i], color=3))

def update_worldclock_dates():
	for i in range(NUMBER_OF_CLOCKFACES):
		string = dec(t_struct[i].tm_year,4) + "-" + dec(t_struct[i].tm_mon,2) + "-" + dec(t_struct[i].tm_mday,2)
		#del worldclock_dates[i]
		worldclock_dates[i] = bitmap_label.Label(FONT, text=string, color=3)

def update_worldclock_days_AMPM():
	for i in range(NUMBER_OF_CLOCKFACES):
		if t_struct[i].tm_hour//12:
			AMPM = " PM"
		else:
			AMPM = " AM"
		string = _DAYNAMES[t_struct[i].tm_wday+1] + AMPM
		#del worldclock_days[i]
		worldclock_days[i] = bitmap_label.Label(FONT, text=string, color=3)

def generate_rotozoom_hands():
	global hour_hand_bitmap
	hour_hand_bitmap = displayio.Bitmap(subbitmap_width, subbitmap_height, palette_colors)
	clear_bitmap(hour_hand_bitmap)
	xs = array.array("i", (subbitmap_center_x-width_of_hour_hand//2, subbitmap_center_x+width_of_hour_hand//2, subbitmap_center_x+width_of_hour_hand//2, subbitmap_center_x-width_of_hour_hand//2))
	ys = array.array("i", (subbitmap_center_y, subbitmap_center_y, subbitmap_center_y-length_of_hour_hand, subbitmap_center_y-length_of_hour_hand))
	bitmaptools.draw_polygon(hour_hand_bitmap, xs, ys, color_of_hour_hand, 2)
	bitmaptools.boundary_fill(hour_hand_bitmap, subbitmap_center_x, subbitmap_center_y-length_of_hour_hand//2, color_of_hour_hand, background_color)
	global minute_hand_bitmap
	minute_hand_bitmap = displayio.Bitmap(subbitmap_width, subbitmap_height, palette_colors)
	clear_bitmap(minute_hand_bitmap)
	xs = array.array("i", (subbitmap_center_x-width_of_minute_hand//2, subbitmap_center_x+width_of_minute_hand//2, subbitmap_center_x+width_of_minute_hand//2, subbitmap_center_x-width_of_minute_hand//2))
	ys = array.array("i", (subbitmap_center_y, subbitmap_center_y, subbitmap_center_y-length_of_minute_hand, subbitmap_center_y-length_of_minute_hand))
	bitmaptools.draw_polygon(minute_hand_bitmap, xs, ys, color_of_minute_hand, 2)
	bitmaptools.boundary_fill(minute_hand_bitmap, subbitmap_center_x, subbitmap_center_y-length_of_minute_hand//2, color_of_minute_hand, background_color)

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
		bitmaptools.draw_polygon(bitmap, xs, ys, color1, 2)
		bitmaptools.boundary_fill(bitmap, (x2+x1)//2, (y2+y1)//2, color1, color2)
	elif "display_shapes"==mode:
		points = []
		points.append((x3, y3))
		points.append((x4, y4))
		points.append((x5, y5))
		points.append((x6, y6))
		object = Polygon(points=points, outline=color1)
		display.root_group.append(object)
		return object

def draw_hour_and_minute_hands(i, hour, minute):
	minute_angle = twopi*minute/60
	hour_angle = twopi*hour12/12
	hour_angle += minute_angle/12
	if "rotozoom"==mode:
		#bitmaptools.blit(bitmap, hour_hand_bitmap, 0, 0)
		#bitmaptools.blit(bitmap, minute_hand_bitmap, 0, 0)
		bitmaptools.rotozoom(bitmap, dots_bitmap, ox=center_x+offset_x[i], oy=center_y+offset_y[i], angle=-rotation_angle)
		#bitmaptools.rotozoom(bitmap, worldclock_titles[i].bitmap, angle=-rotation_angle, skip_index=0, ox=center_x+offset_x[i]+titles_offset_x, oy=center_y+offset_y[i]+titles_offset_y-worldclock_titles[i].bitmap.width//2, scale=FONTSCALE)
		#bitmaptools.rotozoom(bitmap, worldclock_dates[i].bitmap, angle=-rotation_angle, skip_index=0, ox=center_x+offset_x[i]+dates_offset_x, oy=center_y+offset_y[i]+dates_offset_y-worldclock_dates[i].bitmap.width//2, scale=FONTSCALE)
		#bitmaptools.rotozoom(bitmap, worldclock_days[i].bitmap, angle=-rotation_angle, skip_index=0, ox=center_x+offset_x[i]+days_offset_x, oy=center_y+offset_y[i]+days_offset_y-worldclock_days[i].bitmap.width//2, scale=FONTSCALE)
		bitmaptools.rotozoom(bitmap, minute_hand_bitmap, angle=minute_angle-rotation_angle, skip_index=0, ox=center_x+offset_x[i], oy=center_y+offset_y[i])
		bitmaptools.rotozoom(bitmap, hour_hand_bitmap, angle=hour_angle-rotation_angle, skip_index=0, ox=center_x+offset_x[i], oy=center_y+offset_y[i])
	else:
		minute_hand = thickline(subbitmap_center_x, subbitmap_center_y, minute_angle, length_of_minute_hand, width_of_minute_hand, color_of_minute_hand)
		hour_hand = thickline(subbitmap_center_x, subbitmap_center_y, hour_angle, length_of_hour_hand, width_of_hour_hand, color_of_hour_hand)
	#radius_of_middle_dot = max(width_of_minute_hand, width_of_hour_hand)//2 + 1
	#bitmaptools.draw_circle(bitmap, center_x, center_y, radius_of_middle_dot, color_of_dot)
	#bitmaptools.boundary_fill(bitmap, center_x+2, center_y+2, color_of_dot, background_color)
	display.refresh()
	if "bitmaptools"==mode:
		thickline(subbitmap_center_x, subbitmap_center_y, minute_angle, length_of_minute_hand, width_of_minute_hand, background_color, color_of_minute_hand)
		thickline(subbitmap_center_x, subbitmap_center_y, hour_angle, length_of_hour_hand, width_of_hour_hand, background_color, color_of_hour_hand)
	elif "display_shapes"==mode:
		display.root_group.remove(hour_hand)
		display.root_group.remove(minute_hand)
	#diff = time.monotonic() - startup_time; print (str(diff))

setup()
while True:
	update_t_struct()
	for i in range(NUMBER_OF_CLOCKFACES):
		hour24 = t_struct[i].tm_hour
		minute = t_struct[i].tm_min
		second = t_struct[i].tm_sec
		hour12 = hour24 % 12
		print(dec(hour24, 2) + ":" + dec(minute, 2) + ":" + dec(second, 2))
		if 0==minute:
			if "bitmaptools"==mode:
				draw_clockface()
		update_worldclock_dates()
		update_worldclock_days_AMPM()
		draw_hour_and_minute_hands(i, hour12, minute)
	if t_struct[0].tm_hour==23 and t_struct[0].tm_min==59:
		we_still_need_to_get_ntp_time = True
	if we_still_need_to_get_ntp_time:
		print("getting NTP time and setting RTC...")
		get_ntp_time_and_set_RTC()
	gc.collect() ; print(gc.mem_free())
	time.sleep(60 - rtc.RTC().datetime.tm_sec)

