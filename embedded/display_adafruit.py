# last updated 2022-01-18 by mza

import board
import displayio
import terminalio
from adafruit_display_text import label
from DebugInfoWarningError24 import debug, info, warning, error, debug2, debug3, set_verbosity, create_new_logfile_with_string_embedded, flush

def setup_i2c_oled_display_ssd1327(i2c, address):
#	if not should_use_ssd1327_oled_display:
#		return False
	global display
	try:
		import adafruit_ssd1327 # sudo pip3 install adafruit-circuitpython-ssd1327
	except:
		print("unable to find adafruit_ssd1327 library")
		return False
	try:
		display_bus = displayio.I2CDisplay(i2c, device_address=address)
		display = adafruit_ssd1327.SSD1327(display_bus, width=128, height=128)
	except:
		error("can't initialize ssd1327 display over i2c (address " + hex(address) + ")")
		return False
	return True

def setup_i2c_oled_display_sh1107(i2c, address):
#	if not should_use_sh1107_oled_display:
#		return False
	#oled_reset = board.D9
	global display
	try:
		import adafruit_displayio_sh1107
	except:
		print("unable to find adafruit_displayio_sh1107 library")
		return False
	try:
		display_bus = displayio.I2CDisplay(i2c, device_address=address)
		display = adafruit_displayio_sh1107.SH1107(display_bus, width=128, height=64)
		display.auto_refresh = False
	except:
		error("can't initialize sh1107 display over i2c (address " + hex(address) + ")")
		return False
	return True

def clear_display_on_oled_ssd1327():
#	if not oled_display_is_available:
#		return
	global bitmap
	bitmap = displayio.Bitmap(128, 128, 2)
	palette = displayio.Palette(2)
	palette[0] = 0x000000
	palette[1] = 0xffffff
	tile_grid = displayio.TileGrid(bitmap, pixel_shader = palette)
	group = displayio.Group()
	group.append(tile_grid)
	for x in range(128):
		for y in range(128):
			bitmap[x,y] = 0
	display.show(group)
	display.refresh()

def clear_display_on_oled_sh1107():
#	if not oled_display_is_available:
#		return
	global bitmap
	bitmap = displayio.Bitmap(128, 64, 2)
	palette = displayio.Palette(2)
	palette[0] = 0x000000
	palette[1] = 0xffffff
	tile_grid = displayio.TileGrid(bitmap, pixel_shader = palette)
	group = displayio.Group()
	group.append(tile_grid)
	for x in range(128):
		for y in range(64):
			bitmap[x,y] = 0
	display.show(group)
	display.refresh()

def update_temperature_display_on_oled_ssd1327(temperatures_to_plot):
#	if not oled_display_is_available:
#		return
	global bitmap
	display.auto_refresh = False
	rows = 128
	columns = 128
	gain_t = (max_t - offset_t) / (rows - 1)
	for y in range(rows):
		for x in range(columns):
			bitmap[x, y] = 0
	for x in range(columns):
		if 0.0<temperatures_to_plot[x]:
			y = rows - 1 - int((temperatures_to_plot[x] - offset_t) / gain_t)
			if y<0.0:
				y = 0
			if rows<=y:
				y = rows - 1
			bitmap[columns - 1 - x, y] = 1
	display.refresh()

def update_temperature_display_on_oled_sh1107(offset_t, max_t, temperatures_to_plot):
#	if not oled_display_is_available:
#		return
	global bitmap
	display.auto_refresh = False
	rows = 64
	columns = 128
	gain_t = (max_t - offset_t) / (rows - 1)
	for y in range(rows):
		for x in range(columns):
			bitmap[x, y] = 0
	for x in range(columns):
		if 0.0<temperatures_to_plot[x]:
			y = rows - 1 - int((temperatures_to_plot[x] - offset_t) / gain_t)
			if y<0.0:
				y = 0
			if rows<=y:
				y = rows - 1
			bitmap[columns - 1 - x, y] = 1
	display.refresh()

FONTSCALE = 3

def show_text_on_ssd1327(string):
	# https://learn.adafruit.com/adafruit-grayscale-1-5-128x128-oled-display/circuitpython-wiring-and-usage
	splash = displayio.Group()
	display.show(splash)
	text_area = label.Label(terminalio.FONT, text=string, color=0xFFFFFF)
	text_width = text_area.bounding_box[2] * FONTSCALE
	text_group = displayio.Group(
		scale=FONTSCALE,
		x=display.width // 2 - text_width // 2,
		y=display.height // 2,
	)
	text_group.append(text_area)  # Subgroup for text scaling
	splash.append(text_group)
	display.refresh()

def setup_ili9341(spi, tft_cs, tft_dc):
	global display
	try:
		import adafruit_ili9341
	except:
		print("unable to find adafruit_ili9341 library")
		return False
	try:
		displayio.release_displays()
	except:
		pass
	#tft_cs = board.D9
	#tft_dc = board.D10 # conflicts with adalogger cs
	#tft_reset = board.D6
	#sdcard_cs = board.D5
	try:
		display_bus = displayio.FourWire(spi, command=tft_dc, chip_select=tft_cs)
		#display_bus = displayio.FourWire(spi, command=tft_dc, chip_select=tft_cs, reset=tft_reset)
		display = adafruit_ili9341.ILI9341(display_bus, width=320, height=240)
	#	splash = displayio.Group()
	#	display.show(splash)
		return True
	except:
		return False

def setup_st7789(spi, tft_cs, tft_dc, tft_reset):
	global display
	global backlight_pwm
	try:
		import adafruit_st7789
	except:
		print("unable to find adafruit_st7789 library")
		return False
	try:
		displayio.release_displays()
	except:
		pass
	try:
		display_bus = displayio.FourWire(spi, chip_select=tft_cs, command=tft_dc, reset=tft_reset)
		#display_bus = displayio.FourWire(spi, chip_select=tft_cs, command=tft_dc)
		display = adafruit_st7789.ST7789(display_bus, rotation=270, width=240, height=135, rowstart=40, colstart=53)
		return True
	except:
		raise
		return False

def setup_pwm_backlight(backlight_pin, backlight_brightness=0.95):
	try:
		import pwmio
		PWM_MAX = 65535
		backlight_pwm = pwmio.PWMOut(backlight_pin, frequency=5000, duty_cycle=PWM_MAX)
		backlight_pwm.duty_cycle = int(backlight_brightness * PWM_MAX)
	except:
		warning("can't find library pwmio; can't control backlight brightness")

def test_st7789():
	try:
		display
	except:
		display = board.DISPLAY
	BORDER = 20
	FONTSCALE = 2
	BACKGROUND_COLOR = 0x00FF00  # Bright Green
	FOREGROUND_COLOR = 0xAA0088  # Purple
	TEXT_COLOR = 0xFFFF00
	global splash
	splash = displayio.Group()
	display.show(splash)
	info("display show splash")
	color_bitmap = displayio.Bitmap(display.width, display.height, 1)
	color_palette = displayio.Palette(1)
	color_palette[0] = BACKGROUND_COLOR
	bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
	splash.append(bg_sprite)
	info("splash append bg sprite")
	# Draw a smaller inner rectangle
	inner_bitmap = displayio.Bitmap(display.width - BORDER * 2, display.height - BORDER * 2, 1)
	inner_palette = displayio.Palette(1)
	inner_palette[0] = FOREGROUND_COLOR
	inner_sprite = displayio.TileGrid(inner_bitmap, pixel_shader=inner_palette, x=BORDER, y=BORDER)
	splash.append(inner_sprite)
	info("splash append inner sprite")
	# Draw a label
	text = "Hello World!"
	text_area = label.Label(terminalio.FONT, text=text, color=TEXT_COLOR)
	text_width = text_area.bounding_box[2] * FONTSCALE
	text_group = displayio.Group(scale=FONTSCALE, x=display.width // 2 - text_width // 2, y=display.height // 2)
	text_group.append(text_area)  # Subgroup for text scaling
	splash.append(text_group)
	info("splash append text group")
