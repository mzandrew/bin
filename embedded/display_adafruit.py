# last updated 2022-04-27 by mza

import time
import math
import board
import displayio
import terminalio
from adafruit_display_text import label
from DebugInfoWarningError24 import debug, info, warning, error, debug2, debug3, set_verbosity, create_new_logfile_with_string_embedded, flush

display_has_autorefresh = True

def setup_palette(number_of_colors=8, inverted = False):
	global palette2
	global palette8
	palette = displayio.Palette(number_of_colors)
	palette2 = displayio.Palette(2)
	palette8 = displayio.Palette(8)
	palette[0] = 0x000000 # black / background
	palette[1] = 0xffffff # white / foreground
	if 3<number_of_colors:
		palette[2] = 0xff3f3f # red
		palette[3] = 0x00df00 # green
	if 5<number_of_colors:
		palette[4] = 0x3f3fff # blue
		palette[5] = 0xdfdf00 # yellow
	if 7<number_of_colors:
		palette[6] = 0x00efbf # cyan
		palette[7] = 0xff00ff # magenta
	if inverted:
		for i in range(len(palette)):
			palette[i] = 0xffffff - palette[i]
	for i in range(len(palette2)):
		palette2[i] = palette[i]
		palette8[i] = palette[i]
	for i in range(2, len(palette8)):
		j = 1 + (i-1) % (number_of_colors-1) # don't duplicate the background color
		#print(str(i) + " " + str(j))
		palette8[i] = palette[j]

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

def setup_builtin_lcd_hx8357():
	setup_palette()
	global display
	#print("attempting to configure built-in hx8357 lcd...")
	try:
		display = board.DISPLAY
	except:
		print("can't initialize hx8357 display")
		return False
#	try:
#		setup_pwm_backlight(backlight_pin, 1.0)
#	except:
#		print("can't initialize pwm for display backlight")
	#board.DISPLAY.brightness = 0.75
	board.DISPLAY.auto_brightness = True
	#print("complete")
	return True

def setup_builtin_epd():
	setup_palette(2, True)
	global display_has_autorefresh
	display_has_autorefresh = False
	global display
	#print("attempting to configure built-in epd...")
	try:
		display = board.DISPLAY
	except:
		print("can't initialize epd display")
		return False
#	try:
#		setup_pwm_backlight(backlight_pin, 1.0)
#	except:
#		print("can't initialize pwm for display backlight")
	#print("complete")
	return True

def clear_display_on_oled_ssd1327():
#	if not oled_display_is_available:
#		return
	setup_palette()
	global bitmap
	bitmap = displayio.Bitmap(128, 128, 2)
	tile_grid = displayio.TileGrid(bitmap, pixel_shader = palette2)
	group = displayio.Group()
	group.append(tile_grid)
	for x in range(128):
		for y in range(128):
			bitmap[x,y] = 0
	display.show(group)
	refresh()

def clear_display_on_oled_sh1107():
#	if not oled_display_is_available:
#		return
	setup_palette()
	global bitmap
	bitmap = displayio.Bitmap(128, 64, 2)
	tile_grid = displayio.TileGrid(bitmap, pixel_shader = palette2)
	group = displayio.Group()
	group.append(tile_grid)
	for x in range(128):
		for y in range(64):
			bitmap[x,y] = 0
	display.show(group)
	refresh()

def setup_for_n_m_plots(number_of_plots_n, number_of_plots_m, list_of_labels=[[]]):
	number_of_plots = number_of_plots_n * number_of_plots_m
	global display
	display = board.DISPLAY
	if display_has_autorefresh:
		display.auto_refresh = False
	if 1<number_of_plots_n:
		tile_width = display.width//number_of_plots_n
	else:
		tile_width = display.width
	if 1<number_of_plots_m:
		tile_height = display.height//number_of_plots_m
	else:
		tile_height = display.height
	global plot_width
	global plot_height
	padding_size = 24
	plot_width = tile_width - padding_size - 1
	plot_height = tile_height - padding_size - 1
	axes_bitmap = displayio.Bitmap(tile_width, tile_height, 1)
	for i in range(padding_size//2, tile_width-padding_size//2):
		axes_bitmap[i,padding_size//2] = 1
		axes_bitmap[i,tile_height-padding_size//2] = 1
	for j in range(padding_size//2, tile_height-padding_size//2):
		axes_bitmap[padding_size//2,j] = 1
		axes_bitmap[tile_width-padding_size//2,j] = 1
	axes_group = displayio.Group()
	axes = displayio.TileGrid(axes_bitmap, pixel_shader=palette2, width=2, height=2, tile_width=tile_width, tile_height=tile_height, default_tile=0)
	axes_group.append(axes)
	global plot_bitmap
	plot_bitmap = []
	for i in range(number_of_plots):
		plot_bitmap.append(displayio.Bitmap(plot_width, plot_height, 8))
	global plot
	plot = []
	for i in range(number_of_plots):
		plot.append(displayio.TileGrid(plot_bitmap[i], pixel_shader=palette8, width=1, height=1, tile_width=plot_width, tile_height=plot_height, default_tile=0))
	plot_group = displayio.Group()
	for i in range(number_of_plots):
		plot_group.append(plot[i])
	for j in range(number_of_plots_m):
		for i in range(number_of_plots_n):
			n = j*number_of_plots_n+i
			plot[n].x = i * tile_width + padding_size//2 + 1
			plot[n].y = j * tile_height + padding_size//2 + 1
			#print("[" + str(n) + "]=(" + str(plot[n].x) + "," + str(plot[n].y) + ")")
	global group
	group = displayio.Group()
	group.append(axes_group)
	group.append(plot_group)
	FONT_SCALE = 1 # int
	text_area = label.Label(terminalio.FONT, text="i", color=palette2[1]) # 6 pixels each for "W" and "i"
	width_of_single_character = text_area.bounding_box[2] * FONT_SCALE
	FONT_GAP = 2 * width_of_single_character
	#print(str(display.width))
	#print(str(plot_width))
	#print("width of a single character: " + str(width_of_single_character))
	maximum_character_count = 0
	for m in range(len(list_of_labels)):
		character_count = 0
		for n in range(1, len(list_of_labels[m])): # first entry is the plot title
			character_count += len(list_of_labels[m][n])
		number_of_gap_characters = len(list_of_labels[m]) - 2 # first entry is the plot title
		character_count += number_of_gap_characters
		#print(str(character_count))
		if maximum_character_count<character_count:
			maximum_character_count = character_count
	#print(str(maximum_character_count))
	if plot_width<maximum_character_count*width_of_single_character:
		FONT_GAP = FONT_SCALE*width_of_single_character
	#print("font gap: " + str(FONT_GAP))
	for m in range(len(list_of_labels)):
		text_areas = []
		running_text_width = 0
		x = (m%2)*tile_width + tile_width//2
		for n in range(len(list_of_labels[m])):
			#print(list_of_labels[m][n])
			if n==0:
				y = (m//2)*tile_height + FONT_SCALE * 5
				text_area = label.Label(terminalio.FONT, text=list_of_labels[m][n], color=palette8[1]) # white for plot label
				text_width = text_area.bounding_box[2] * FONT_SCALE
				text_group = displayio.Group(scale=FONT_SCALE, x=x-text_width//2, y=y)
				text_group.append(text_area)
				group.append(text_group)
			else:
				text_area = label.Label(terminalio.FONT, text=list_of_labels[m][n], color=palette8[n+1]) # other colors
				text_width = text_area.bounding_box[2] * FONT_SCALE + FONT_GAP
				running_text_width += text_width
				text_areas.append(text_area)
		y = (m//2)*tile_height + tile_height - FONT_SCALE * 5 - 2
		x -= running_text_width//2
		x += FONT_GAP//2
		for text_area in text_areas:
			text_width = text_area.bounding_box[2] * FONT_SCALE + FONT_GAP
			text_group = displayio.Group(scale=FONT_SCALE, x=x, y=y)
			x += text_width
			text_group.append(text_area)
			group.append(text_group)
	display.show(group)

def refresh():
	try:
		display.refresh()
		#info("worked immediately")
	except:
		time.sleep(0.05)
		try:
			display.refresh()
			#info("worked after 50 ms")
		except:
			pass

def format_for_plot(values, minimum, maximum):
	new_values = []
	#print(str(values))
	for i in range(len(values)):
		new_values.append((values[i]-minimum)/(maximum - minimum))
	return new_values

# arrays to plot should be plot_width elements deep and go from 0.0 to 1.0
def update_plot(plot_number, arrays_to_plot):
	for x in range(plot_width):
		for y in range(plot_height):
			plot_bitmap[plot_number][x,y] = 0
			for n in range(len(arrays_to_plot)):
				if plot_width<len(arrays_to_plot[n]):
					array_to_plot = arrays_to_plot[n][-plot_width:]
				else:
					array_to_plot = arrays_to_plot[n]
				yn = int(0. + plot_height - 1. * plot_height * array_to_plot[x])
				doit = False
				if y==yn:
					doit = True
				elif 0==y and yn<0:
					doit = True
				elif plot_height-1==y and plot_height<yn:
					doit = True
				if doit:
					plot_bitmap[plot_number][x,y] = n + 2 # first two indices are black and white

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
	refresh()

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
	refresh()

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
	refresh()

def setup_ili9341(spi, tft_cs, tft_dc):
	global display
	try:
		import adafruit_ili9341
	except:
		print("unable to find adafruit_ili9341 library")
		return False
#	try:
#		displayio.release_displays()
#	except:
#		pass
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
	#global backlight_pwm
	try:
		import adafruit_st7789
	except:
		print("unable to find adafruit_st7789 library")
		return False
#	try:
#		displayio.release_displays()
#	except:
#		pass
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
	except:
		warning("can't find library pwmio; can't control backlight brightness")
	PWM_MAX = 65535
	try:
		backlight_pwm = pwmio.PWMOut(backlight_pin, frequency=5000, duty_cycle=PWM_MAX)
		backlight_pwm.duty_cycle = int(backlight_brightness * PWM_MAX)
	except:
		warning("can't initialize display backlight pwm pin")

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

