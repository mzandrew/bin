#!/usr/bin/env python3

# written 2022-04-23 by mza
# based on temperature_log_and_graph.py
# last updated 2022-04-27 by mza

# to install on a circuitpython device:
# rsync -av *.py /media/mza/CIRCUITPY/; cp -a weather_station_portal.py /media/mza/CIRCUITPY/code.py ; sync
# ln -s ~/build/adafruit-circuitpython/bundle/lib
# cd lib
# rsync -r adafruit_minimqtt adafruit_magtag adafruit_bitmap_font adafruit_portalbase adafruit_display_text adafruit_esp32spi adafruit_register neopixel.mpy adafruit_rgbled.mpy adafruit_requests.mpy adafruit_sdcard.mpy simpleio.mpy adafruit_io /media/circuitpython/lib/
# sync

import time
import sys
import atexit
import board
import busio
import displayio
import airlift

import microsd_adafruit
import neopixel_adafruit
try:
	from DebugInfoWarningError24 import debug, info, warning, error, debug2, debug3, set_verbosity, create_new_logfile_with_string_embedded, flush
except:
	print("can't find DebugInfoWarningError24.py")
	sys.exit(0)
import generic
import display_adafruit
#import adafruit_touchscreen

board_id = board.board_id
info("we are " + board_id)
if board_id=="pyportal_titano" or board_id=="pyportal":
	delay = 1.0 # number of seconds between updates
	plots_to_update_every_screen_refresh = 1
	should_use_airlift = True
	should_use_builtin_wifi = False
	should_use_epd = False
	should_use_hx8357_lcd = True
	should_use_sdcard = True
	should_use_RTC = False
	should_use_SPI = True
elif board_id=="adafruit_magtag_2.9_grayscale":
	delay = 1.0 # number of seconds between updates
	plots_to_update_every_screen_refresh = 4
	should_use_airlift = False
	should_use_builtin_wifi = True
	should_use_epd = True
	should_use_hx8357_lcd = False
	should_use_sdcard = False
	should_use_RTC = False
	should_use_SPI = False
else:
	error("what board am I?")

MIN_TEMP_TO_PLOT = 10.0
MAX_TEMP_TO_PLOT = 80.0
MIN_HUM_TO_PLOT = 40.0
MAX_HUM_TO_PLOT = 100.0
MIN_PRES_TO_PLOT = 0.997
MAX_PRES_TO_PLOT = 1.008
MIN_PARTICLE_COUNT_TO_PLOT = 0.0
MAX_PARTICLE_COUNT_TO_PLOT = 350.0

dirname = "/logs"
loop_counter = 0

def loop():
	#print("loop(" + str(loop_counter) + ")")
	#display_adafruit.update_four_plots(loop_counter)
	update_plot = [ False, False, False, False ]
	if 1==plots_to_update_every_screen_refresh:
		lcm4 = loop_counter%4
		if 0==lcm4:
			update_plot[0] = True
			if airlift_is_available:
				string = airlift.get_time_string_from_server()
				info(string)
		elif 1==lcm4:
			update_plot[1] = True
		elif 2==lcm4:
			update_plot[2] = True
		else:
			update_plot[3] = True
	else:
		update_plot = [ True, True, True, True ]
		if airlift_is_available:
			string = airlift.get_time_string_from_server()
			info(string)
	if update_plot[0]:
		info("updating temperatures...")
		global ds18b20
		ds18b20 = airlift.add_most_recent_data_to_end_of_array(ds18b20, "roof-ds18b20")
		myarray_a = display_adafruit.format_for_plot(ds18b20, MIN_TEMP_TO_PLOT, MAX_TEMP_TO_PLOT)
		global temperature_outdoor
		temperature_outdoor = airlift.add_most_recent_data_to_end_of_array(temperature_outdoor, "outdoor-temp")
		myarray_b = display_adafruit.format_for_plot(temperature_outdoor, MIN_TEMP_TO_PLOT, MAX_TEMP_TO_PLOT)
		global temperature_indoor
		temperature_indoor = airlift.add_most_recent_data_to_end_of_array(temperature_indoor, "inside-temp")
		myarray_c = display_adafruit.format_for_plot(temperature_indoor, MIN_TEMP_TO_PLOT, MAX_TEMP_TO_PLOT)
		global heater
		heater = airlift.add_most_recent_data_to_end_of_array(heater, "heater")
		myarray_d = display_adafruit.format_for_plot(heater, MIN_TEMP_TO_PLOT, MAX_TEMP_TO_PLOT)
		display_adafruit.update_plot(0, [myarray_c, myarray_b, myarray_a, myarray_d])
	if update_plot[1]:
		info("updating humidities...")
		global sht31d
		sht31d = airlift.add_most_recent_data_to_end_of_array(sht31d, "roof-hum")
		myarray_a = display_adafruit.format_for_plot(sht31d, MIN_HUM_TO_PLOT, MAX_HUM_TO_PLOT)
		global humidity_outdoor
		humidity_outdoor = airlift.add_most_recent_data_to_end_of_array(humidity_outdoor, "outdoor-hum")
		myarray_b = display_adafruit.format_for_plot(humidity_outdoor, MIN_HUM_TO_PLOT, MAX_HUM_TO_PLOT)
		global humidity_indoor
		humidity_indoor = airlift.add_most_recent_data_to_end_of_array(humidity_indoor, "inside-hum")
		myarray_c = display_adafruit.format_for_plot(humidity_indoor, MIN_HUM_TO_PLOT, MAX_HUM_TO_PLOT)
		display_adafruit.update_plot(1, [myarray_c, myarray_b, myarray_a])
	if update_plot[2]:
		info("updating pressures...")
		global pressure
		pressure = airlift.add_most_recent_data_to_end_of_array(pressure, "pressure")
		myarray_a = display_adafruit.format_for_plot(pressure, MIN_PRES_TO_PLOT, MAX_PRES_TO_PLOT)
		display_adafruit.update_plot(2, [myarray_a])
	if update_plot[3]:
		info("updating particle counts...")
		global particle0p3
		particle0p3 = airlift.add_most_recent_data_to_end_of_array(particle0p3, "particle0p3")
		myarray_a = display_adafruit.format_for_plot(particle0p3, MIN_PARTICLE_COUNT_TO_PLOT, MAX_PARTICLE_COUNT_TO_PLOT)
		global particle0p5
		particle0p5 = airlift.add_most_recent_data_to_end_of_array(particle0p5, "particle0p5")
		myarray_b = display_adafruit.format_for_plot(particle0p5, MIN_PARTICLE_COUNT_TO_PLOT, MAX_PARTICLE_COUNT_TO_PLOT)
		global particle1p0
		particle1p0 = airlift.add_most_recent_data_to_end_of_array(particle1p0, "particle1p0")
		myarray_c = display_adafruit.format_for_plot(particle1p0, MIN_PARTICLE_COUNT_TO_PLOT, MAX_PARTICLE_COUNT_TO_PLOT)
		global particle2p5
		particle2p5 = airlift.add_most_recent_data_to_end_of_array(particle2p5, "particle2p5")
		myarray_d = display_adafruit.format_for_plot(particle2p5, MIN_PARTICLE_COUNT_TO_PLOT, MAX_PARTICLE_COUNT_TO_PLOT)
		global particle5p0
		particle5p0 = airlift.add_most_recent_data_to_end_of_array(particle5p0, "particle5p0")
		myarray_e = display_adafruit.format_for_plot(particle5p0, MIN_PARTICLE_COUNT_TO_PLOT, MAX_PARTICLE_COUNT_TO_PLOT)
		display_adafruit.update_plot(3, [myarray_a, myarray_b, myarray_c, myarray_d, myarray_e])
	display_adafruit.refresh()
	flush()
	time.sleep(delay)

def main():
#	try:
#		displayio.release_displays() # this is what stops terminalio from functioning
#	except:
#		pass
	global neopixel_is_available
	try:
		neopixel_is_available = neopixel_adafruit.setup_neopixel()
	except (KeyboardInterrupt, ReloadException):
		raise
	except:
		error("error setting up neopixel")
		neopixel_is_available = False
	if neopixel_is_available:
		neopixel_adafruit.set_color(127, 127, 127)
	global i2c
	try:
		i2c = board.I2C
	except (KeyboardInterrupt, ReloadException):
		raise
	except:
		try:
			i2c = busio.I2C(board.SCL1, board.SDA1)
			info("using I2C1")
		except:
			i2c = busio.I2C(board.SCL, board.SDA)
			info("using I2C0")
#	try:
#		setup_temperature_sensors(i2c)
#	except:
#		error("can't find any temperature sensors on i2c bus")
	global display_is_available
	if should_use_hx8357_lcd:
		display_is_available = display_adafruit.setup_builtin_lcd_hx8357()
	if should_use_epd:
		display_is_available = display_adafruit.setup_builtin_epd()
	global RTC_is_available
	if should_use_RTC:
		RTC_is_available = pcf8523_adafruit.setup(i2c)
	else:
		RTC_is_available = False
	global spi
#	try:
#		spi = board.SPI
#	except:
	if should_use_SPI:
		#try:
		#	spi = board.SPI # this does not work for the pyportal board
		#except:
		spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
	global airlift_is_available
	if should_use_airlift:
		airlift_is_available = airlift.setup_airlift("weather-station-portal", spi, board.ESP_CS, board.ESP_BUSY, board.ESP_RESET)
	elif should_use_builtin_wifi:
		airlift_is_available = airlift.setup_wifi("weather-station-portal")
	else:
		airlift_is_available = False
	if not airlift_is_available:
		error("can't connect to wifi - rebooting in 10 seconds...")
		flush()
		time.sleep(10)
		generic.reset()
	global sdcard_is_available
	global dirname
	if should_use_sdcard:
		sdcard_is_available = microsd_adafruit.setup_sdcard_for_logging_data(spi, board.SD_CS, dirname)
	else:
		sdcard_is_available = False
		dirname = ""
	if RTC_is_available:
		create_new_logfile_with_string_embedded(dirname, "weather_station", pcf8523_adafruit.get_timestring2())
	else:
		create_new_logfile_with_string_embedded(dirname, "weather_station")
	display_adafruit.setup_for_n_m_plots(2, 2, [["temperature", "indoor", "outdoor", "roof", "heater"], ["humidity", "indoor", "outdoor", "roof"], ["pressure", "indoor"], ["particle count", "0.3", "0.5", "1.0", "2.5", "5.0"]])
	display_adafruit.refresh()
	array_size = display_adafruit.plot_width
	if 1:
		global ds18b20
		global temperature_outdoor
		global temperature_indoor
		global heater
		global sht31d
		global humidity_outdoor
		global humidity_indoor
		global pressure
		global particle0p3
		global particle0p5
		global particle1p0
		global particle2p5
		global particle5p0
		ds18b20 = [ -40.0 for i in range(array_size) ]
		temperature_outdoor = [ -40.0 for i in range(array_size) ]
		temperature_indoor = [ -40.0 for i in range(array_size) ]
		heater = [ -40.0 for i in range(array_size) ]
		sht31d = [ -40.0 for i in range(array_size) ]
		humidity_outdoor = [ -40.0 for i in range(array_size) ]
		humidity_indoor = [ -40.0 for i in range(array_size) ]
		pressure = [ -40.0 for i in range(array_size) ]
		particle0p3 = [ -40.0 for i in range(array_size) ]
		particle0p5 = [ -40.0 for i in range(array_size) ]
		particle1p0 = [ -40.0 for i in range(array_size) ]
		particle2p5 = [ -40.0 for i in range(array_size) ]
		particle5p0 = [ -40.0 for i in range(array_size) ]
	if 0:
		print("fetching old data from feeds...")
		#global temperature_indoor
		#temperature_indoor = airlift.get_all_data("inside-temp", array_size)
		global humidity_indoor
		humidity_indoor = airlift.get_all_data("inside-hum", array_size)
		print(str(humidity_indoor))
	global loop_counter
	while True:
		loop()
		loop_counter += 1
	error("pct2075 is not present")
	if neopixel_is_available:
		neopixel_adafruit.set_color(0, 255, 255)

if __name__ == "__main__":
	#supervisor.disable_autoreload()
	generic.register_atexit_handler()
	try:
		main()
	except KeyboardInterrupt:
		generic.keyboard_interrupt_exception_handler()
	except ReloadException:
		generic.reload_exception_handler()
	info("leaving program...")
	flush()
	generic.reset()

