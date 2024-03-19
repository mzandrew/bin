#!/usr/bin/env python3

# written 2024-01-18 by mza
# based on 480x320-tft-feather-clock.py, bar320x960-ips-clock.py, round40-ips-clock.py, 64x64-rgbmatrix-clock.py
# from https://learn.adafruit.com/rgb-matrix-slot-machine/circuitpython-libraries
# and https://learn.adafruit.com/rgb-led-matrices-matrix-panels-with-circuitpython/advanced-multiple-panels
# last updated 2024-03-16 by mza

# for use on an interstate75w (raspberry_pi_pico_w) with a rgbmatrix
# or for use on a adafruit_qualia_s3_rgb666 with a rgb 666 tft display
# or for use on a adafruit_feather_esp32s2 or a feather-esp32-v2 with a tft feather

# to install:
# rsync -av adafruit_qualia adafruit_portalbase adafruit_bitmap_font adafruit_io adafruit_minimqtt adafruit_bus_device adafruit_display_text adafruit_display_shapes adafruit_fakerequests.mpy adafruit_requests.mpy adafruit_pca9554.mpy adafruit_focaltouch.mpy adafruit_cst8xx.mpy adafruit_hx8357.mpy adafruit_tsc2007.mpy adafruit_datetime.mpy adafruit_ntp.mpy /media/mza/CIRCUITPY/lib/
# cp -a settings.toml /media/mza/CIRCUITPY/
# cp -a 64x32-matrix-clock.py /media/mza/CIRCUITPY/code.py; sync
# customize custom_label.boot.py with "64X64CLOCK" or "720X720CLOC" (as appropriate), unmount CIRCUITPY drive and unplug/replug board

#import adafruit_tsc2007
#i2c = board.STEMMA_I2C()
#irq_dio = None
#tsc = adafruit_tsc2007.TSC2007(i2c, irq=irq_dio)

import math
import storage
import re
import gc
import array
import time
import board
import rtc
import displayio
from adafruit_display_shapes.circle import Circle
from adafruit_display_shapes.polygon import Polygon
from adafruit_display_text import bitmap_label
from adafruit_datetime import _DAYNAMES
from terminalio import FONT
import bitmaptools

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

#peripherals = Peripherals()
#peripherals.backlight = True
fake_the_network_being_down_counter = 0
#mode = "bitmaptools"
#mode = "display_shapes"
mode = "rotozoom"

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

def hang():
	while True:
		time.sleep(1)

def setup():
	print()
	print("board type: " + board.board_id)
	m = storage.getmount("/")
	label = m.label
	print("label is: " + label)
	numV = 1 # tiling in vertical direction
	numH = 1 # tiling in horizontal direction
	match = re.search("([0-9]+)X([0-9]+)CLOC", str(label)) # "64X64CLOCK"
	if match:
		width = int(match.group(1))
		height = int(match.group(2))
		print("width: " + str(width))
		print("height: " + str(height))
	else:
		match = re.search("([0-9]+)X([0-9]+)X([0-9]+)", str(label)) # "64X32X2" (implicit vertical tiling)
		if match:
			width = int(match.group(1))
			height = int(match.group(2))
			numV = int(match.group(3))
			print("width: " + str(width))
			print("height: " + str(height))
			print("numV: " + str(numV))
		else:
			match = re.search("([0-9]+)X([0-9]+)X([0-9]+)X([0-9]|)", str(label)) # "64X64X2X2"
			if match:
				width = int(match.group(1))
				height = int(match.group(2))
				numH = int(match.group(3))
				numV = int(match.group(4))
				print("width: " + str(width))
				print("height: " + str(height))
				print("numH: " + str(numH))
				print("numV: " + str(numV))
			else:
				print("customize custom_label.boot.py with \"64X64CLOCK\" or \"320x480CLOCK\" or \"63X32X2\" (etc)")
				print("then cp custom_label.boot.py to /media/mza/CIRCUITPY/boot.py")
				print("unmount drive, and then unplug/replug board")
				hang()
	global NTP_INDEX, should_show_worldclock_labels, subbitmap_width, subbitmap_height
	global length_of_hour_hand, length_of_minute_hand, distance_of_dot_from_center, radius_of_dot
	global width_of_hour_hand, width_of_minute_hand, subbitmap_center_x, subbitmap_center_y
	global FONTSCALE, titles_offset_x, titles_offset_y, dates_offset_x, dates_offset_y, days_offset_x, days_offset_y
	global rotation_angle, twopi, color_of_dot, NUMBER_OF_CLOCKFACES
	global worldclock_text, offset_timezone, offset_x, offset_y
	if numH*width==64 and numV*height==32:
		subbitmap_size = 32
		brightness = 0.4
		rotation_angle = 0*math.pi/2
		boardtype = "rgbmatrix"
		should_show_worldclock_labels = False
		color_of_dot = 4
		radius_of_dot = 0.75
		width_of_hour_hand = 1.75
		width_of_minute_hand = 0.25
		distance_of_dot_from_center = 14.5
	elif numH*width==64 and numV*height==64:
		subbitmap_size = 64
		brightness = 0.25
		rotation_angle = 0*math.pi/2
		boardtype = "rgbmatrix"
		should_show_worldclock_labels = False
		color_of_dot = 4
		radius_of_dot = 0
		width_of_hour_hand = 2
		width_of_minute_hand = 2
		distance_of_dot_from_center = 31
	elif width==480 and height==320:
		subbitmap_size = 320
		rotation_angle = 3*math.pi/2
		boardtype = "feather"
		should_show_worldclock_labels = True
		color_of_dot = 5
		radius_of_dot = 7
		width_of_hour_hand = 16
		width_of_minute_hand = 9
		distance_of_dot_from_center = 148
	elif width==320 and height==960:
		rotation_angle = 1*math.pi/2 # must come after 320 one above
		subbitmap_size = 320
		boardtype = "qualia"
		should_show_worldclock_labels = True
		color_of_dot = 4
		radius_of_dot = 7
		width_of_hour_hand = 16
		width_of_minute_hand = 9
		distance_of_dot_from_center = 148
	elif width==720 and height==720:
		subbitmap_size = 720
		boardtype = "qualia"
		rotation_angle = 0*math.pi/2
		should_show_worldclock_labels = False
		color_of_dot = 4
		radius_of_dot = 10
		width_of_hour_hand = 24
		width_of_minute_hand = 16
		distance_of_dot_from_center = 342
	else:
		print("unsupported width/height combination (1)")
		hang()
	subbitmap_width = subbitmap_size
	subbitmap_height = subbitmap_size
	length_of_hour_hand = int(0.45 * subbitmap_size/2)
	length_of_minute_hand = int(0.85 * subbitmap_size/2)
	subbitmap_center_x = subbitmap_width//2
	subbitmap_center_y = subbitmap_height//2
	FONTSCALE = 2
	if width==480:
		titles_offset_x = 150
		titles_offset_y = -50
		dates_offset_x = -200
		dates_offset_y = -52
		days_offset_x = -200
		days_offset_y = 77
	elif subbitmap_size==320:
		titles_offset_x = -150
		titles_offset_y = -50
		dates_offset_x = 150
		dates_offset_y = -52
		days_offset_x = 150
		days_offset_y = 77
	if height==3*width: # worldclock mode
		NUMBER_OF_CLOCKFACES = 3
		worldclock_text = [ "Tokyo", "Honolulu", "New York" ]
		offset_timezone = [ +19, 0, +5 ]
		offset_x = [ 0, 0, 0 ]
		offset_y = [ 320, 0, -320 ]
		NTP_INDEX = 1
		rotation_angle = 1*math.pi/2
	else:
		NUMBER_OF_CLOCKFACES = 1
		worldclock_text = [ " " ]
		offset_timezone = [ 0 ]
		offset_x = [ 0 ]
		offset_y = [ 0 ]
		NTP_INDEX = 0
	#global startup_time; startup_time = time.monotonic()
	global twopi; twopi = 2 * math.pi
	global display, bitmap
	gc.collect(); print(gc.mem_free())
	displayio.release_displays()
	if boardtype=="qualia":
		from adafruit_qualia.graphics import Graphics, Displays # helps find the name "Displays.BAR320X960"
		from adafruit_qualia.peripherals import Peripherals
		if width==320 and height==960:
			graphics = Graphics(Displays.BAR320X960, default_bg=None, auto_refresh=False)
		elif width==720 and height==720:
			graphics = Graphics(Displays.ROUND40, default_bg=None, auto_refresh=False)
		else:
			print("unsupported width/height combination (2)")
			hang()
		display = graphics.display
		splash = graphics.splash
	elif boardtype=="feather":
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
	elif boardtype=="rgbmatrix":
		import rgbmatrix
		import framebufferio
		if 0:
			matrix = rgbmatrix.RGBMatrix( # matrix_featherwing
				width=64, height=32, bit_depth=4,
				rgb_pins=[board.D6, board.D5, board.D9, board.D11, board.D10, board.D12], # R1, G1, B1, R2, B2, G2
				addr_pins=[board.A5, board.A4, board.A3, board.A2], # ROW_A, ROW_B, ROW_C, ROW_D
				clock_pin=board.D13, latch_pin=board.D0, output_enable_pin=board.D1)
		elif width==64 and height==32:
			try:
				matrix = rgbmatrix.RGBMatrix( # pimoroni_interstate75 64x32
					width=numH*width, height=numV*height, bit_depth=4, tile=numV,
					rgb_pins=[board.R0, board.G0, board.B0, board.R1, board.G1, board.B1], # R0, G0, B0, R1, G1, B1
					addr_pins=[board.ROW_A, board.ROW_B, board.ROW_C, board.ROW_D], # ROW_E needed for 64x64 displays
					clock_pin=board.CLK, latch_pin=board.LAT, output_enable_pin=board.OE)
			except:
				matrix = rgbmatrix.RGBMatrix( # interstate75w 64x32
					width=numH*width, height=numV*height, bit_depth=4, tile=numV,
					rgb_pins=[board.GP0, board.GP1, board.GP2, board.GP3, board.GP4, board.GP5], # R0, G0, B0, R1, G1, B1
					addr_pins=[board.GP6, board.GP7, board.GP8, board.GP9], # ROW_E needed for 64x64 displays
					clock_pin=board.GP11, latch_pin=board.GP12, output_enable_pin=board.GP13)
		elif width==64 and height==64:
			try:
				matrix = rgbmatrix.RGBMatrix( # pimoroni_interstate75 64x64
					width=numH*width, height=numV*height, bit_depth=4, tile=numV,
					rgb_pins=[board.R0, board.G0, board.B0, board.R1, board.G1, board.B1], # R0, G0, B0, R1, G1, B1
					addr_pins=[board.ROW_A, board.ROW_B, board.ROW_C, board.ROW_D, board.ROW_E], # ROW_E needed for 64x64 displays
					clock_pin=board.CLK, latch_pin=board.LAT, output_enable_pin=board.OE)
			except:
				matrix = rgbmatrix.RGBMatrix( # interstate75w 64x64
					width=numH*width, height=numV*height, bit_depth=4, tile=numV,
					rgb_pins=[board.GP0, board.GP1, board.GP2, board.GP3, board.GP4, board.GP5], # R0, G0, B0, R1, G1, B1
					addr_pins=[board.GP6, board.GP7, board.GP8, board.GP9, board.GP10], # ROW_E needed for 64x64 displays
					clock_pin=board.GP11, latch_pin=board.GP12, output_enable_pin=board.GP13)
		else:
			print("unsupported width/height combination (3)")
			hang()
		matrix.brightness = brightness
		# ValueError: 5 address pins, 6 rgb pins and 1 tiles indicate a height of 64, not 32
		splash = displayio.Group()
		display = framebufferio.FramebufferDisplay(matrix)
	else:
		print("unsupported width/height combination (4)")
		hang()
	#display.auto_refresh = False
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
	xs = array.array("i", (int(subbitmap_center_x-width_of_hour_hand/2), int(subbitmap_center_x+width_of_hour_hand/2), int(subbitmap_center_x+width_of_hour_hand/2), int(subbitmap_center_x-width_of_hour_hand/2)))
	ys = array.array("i", (subbitmap_center_y, subbitmap_center_y, int(subbitmap_center_y-length_of_hour_hand), int(subbitmap_center_y-length_of_hour_hand)))
	bitmaptools.draw_polygon(hour_hand_bitmap, xs, ys, color_of_hour_hand, 2)
	bitmaptools.boundary_fill(hour_hand_bitmap, subbitmap_center_x, int(subbitmap_center_y-length_of_hour_hand/2), color_of_hour_hand, background_color)
	global minute_hand_bitmap
	minute_hand_bitmap = displayio.Bitmap(subbitmap_width, subbitmap_height, palette_colors)
	clear_bitmap(minute_hand_bitmap)
	xs = array.array("i", (int(subbitmap_center_x-width_of_minute_hand/2), int(subbitmap_center_x+width_of_minute_hand/2), int(subbitmap_center_x+width_of_minute_hand/2), int(subbitmap_center_x-width_of_minute_hand/2)))
	ys = array.array("i", (subbitmap_center_y, subbitmap_center_y, int(subbitmap_center_y-length_of_minute_hand), int(subbitmap_center_y-length_of_minute_hand)))
	bitmaptools.draw_polygon(minute_hand_bitmap, xs, ys, color_of_minute_hand, 2)
	bitmaptools.boundary_fill(minute_hand_bitmap, subbitmap_center_x, int(subbitmap_center_y-length_of_minute_hand/2), color_of_minute_hand, background_color)

def thickline(x1, y1, angle, length, width, color1, color2=background_color):
	x2 = x1 + int(length*math.sin(angle))
	y2 = y1 - int(length*math.cos(angle))
	#return Line(x1, y1, x2, y2, color1)
	#return Polygon(points=[(x1, y1), (x2, y2)], outline=color1)
	x_adjustment = int(width/2*math.cos(angle))
	y_adjustment = int(width/2*math.sin(angle))
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
		if should_show_worldclock_labels:
			bitmaptools.rotozoom(bitmap, worldclock_titles[i].bitmap, angle=-rotation_angle, skip_index=0, ox=center_x+offset_x[i]+titles_offset_x, oy=center_y+offset_y[i]+titles_offset_y-worldclock_titles[i].bitmap.width//2, scale=FONTSCALE)
			bitmaptools.rotozoom(bitmap, worldclock_dates[i].bitmap, angle=-rotation_angle, skip_index=0, ox=center_x+offset_x[i]+dates_offset_x, oy=center_y+offset_y[i]+dates_offset_y-worldclock_dates[i].bitmap.width//2, scale=FONTSCALE)
			bitmaptools.rotozoom(bitmap, worldclock_days[i].bitmap, angle=-rotation_angle, skip_index=0, ox=center_x+offset_x[i]+days_offset_x, oy=center_y+offset_y[i]+days_offset_y-worldclock_days[i].bitmap.width//2, scale=FONTSCALE)
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
	if t_struct[NTP_INDEX].tm_hour==23 and t_struct[NTP_INDEX].tm_min==59:
		we_still_need_to_get_ntp_time = True
	if we_still_need_to_get_ntp_time:
		print("getting NTP time and setting RTC...")
		get_ntp_time_and_set_RTC()
	gc.collect() ; print(gc.mem_free())
	time.sleep(60 - rtc.RTC().datetime.tm_sec)

