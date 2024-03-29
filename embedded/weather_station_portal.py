#!/usr/bin/env python3

# written 2022-04-23 by mza
# based on temperature_log_and_graph.py
# last updated 2023-01-08 by mza

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
import gc
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
	delay = 125 # number of seconds between updates; 4*125=500
	plots_to_update_every_screen_refresh = 1
	should_use_airlift = True
	should_use_builtin_wifi = False
	should_use_epd = False
	should_use_hx8357_lcd = True
	should_use_sdcard = True
	should_use_RTC = False
	should_use_SPI = True
elif board_id=="adafruit_magtag_2.9_grayscale":
	delay = 500 # number of seconds between updates
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
#			if airlift_is_available:
#				string = airlift.get_time_string_from_server()
#				info(string)
		elif 1==lcm4:
			update_plot[1] = True
		elif 2==lcm4:
			update_plot[2] = True
		else:
			update_plot[3] = True
	else:
		update_plot = [ True, True, True, True ]
#		if airlift_is_available:
#			string = airlift.get_time_string_from_server()
#			info(string)
	if update_plot[0]:
		info("updating temperatures...")
		global temperature_indoor
		temperature_indoor = airlift.add_most_recent_data_to_end_of_array(temperature_indoor, "living-room-temp")
		myarray_a = display_adafruit.format_for_plot(temperature_indoor, MIN_TEMP_TO_PLOT, MAX_TEMP_TO_PLOT)
		global temperature_3dprinter
		temperature_3dprinter = airlift.add_most_recent_data_to_end_of_array(temperature_3dprinter, "3d-printer-temp")
		myarray_b = display_adafruit.format_for_plot(temperature_3dprinter, MIN_TEMP_TO_PLOT, MAX_TEMP_TO_PLOT)
		global temperature_outdoor
		temperature_outdoor = airlift.add_most_recent_data_to_end_of_array(temperature_outdoor, "outdoor-temp")
		myarray_c = display_adafruit.format_for_plot(temperature_outdoor, MIN_TEMP_TO_PLOT, MAX_TEMP_TO_PLOT)
		global ds18b20
		ds18b20 = airlift.add_most_recent_data_to_end_of_array(ds18b20, "roof-temp")
		myarray_d = display_adafruit.format_for_plot(ds18b20, MIN_TEMP_TO_PLOT, MAX_TEMP_TO_PLOT)
		global heater
		heater = airlift.add_most_recent_data_to_end_of_array(heater, "heater")
		myarray_e = display_adafruit.format_for_plot(heater, MIN_TEMP_TO_PLOT, MAX_TEMP_TO_PLOT)
		display_adafruit.update_plot(0, [myarray_a, myarray_b, myarray_c, myarray_d, myarray_e])
	if update_plot[1]:
		info("updating humidities...")
		global humidity_living_room
		humidity_living_room = airlift.add_most_recent_data_to_end_of_array(humidity_living_room, "living-room-hum")
		myarray_a = display_adafruit.format_for_plot(humidity_living_room, MIN_HUM_TO_PLOT, MAX_HUM_TO_PLOT)
		global humidity_indoor
		humidity_indoor = airlift.add_most_recent_data_to_end_of_array(humidity_indoor, "3d-printer-hum")
		myarray_b = display_adafruit.format_for_plot(humidity_indoor, MIN_HUM_TO_PLOT, MAX_HUM_TO_PLOT)
		global humidity_outdoor
		humidity_outdoor = airlift.add_most_recent_data_to_end_of_array(humidity_outdoor, "outdoor-hum")
		myarray_c = display_adafruit.format_for_plot(humidity_outdoor, MIN_HUM_TO_PLOT, MAX_HUM_TO_PLOT)
		global sht31d
		sht31d = airlift.add_most_recent_data_to_end_of_array(sht31d, "roof-hum")
		myarray_d = display_adafruit.format_for_plot(sht31d, MIN_HUM_TO_PLOT, MAX_HUM_TO_PLOT)
		display_adafruit.update_plot(1, [myarray_a, myarray_b, myarray_c, myarray_d])
	if update_plot[2]:
		info("updating pressures...")
		global pressure_living_room
		pressure_living_room = airlift.add_most_recent_data_to_end_of_array(pressure_living_room, "living-room-pressure")
		myarray_a = display_adafruit.format_for_plot(pressure_living_room, MIN_PRES_TO_PLOT, MAX_PRES_TO_PLOT)
		global pressure
		pressure = airlift.add_most_recent_data_to_end_of_array(pressure, "3d-printer-pressure")
		myarray_b = display_adafruit.format_for_plot(pressure, MIN_PRES_TO_PLOT, MAX_PRES_TO_PLOT)
		display_adafruit.update_plot(2, [myarray_a, myarray_b])
	if update_plot[3]:
		info("updating particle counts...")
		#global particle0p3
		#particle0p3 = airlift.add_most_recent_data_to_end_of_array(particle0p3, "garage-0p3")
		#myarray_a = display_adafruit.format_for_plot(particle0p3, MIN_PARTICLE_COUNT_TO_PLOT, MAX_PARTICLE_COUNT_TO_PLOT)
		#global particle0p5
		#particle0p5 = airlift.add_most_recent_data_to_end_of_array(particle0p5, "garage-0p5")
		#myarray_b = display_adafruit.format_for_plot(particle0p5, MIN_PARTICLE_COUNT_TO_PLOT, MAX_PARTICLE_COUNT_TO_PLOT)
		global particle1p0
		particle1p0 = airlift.add_most_recent_data_to_end_of_array(particle1p0, "garage-1p0")
		myarray_c = display_adafruit.format_for_plot(particle1p0, MIN_PARTICLE_COUNT_TO_PLOT, MAX_PARTICLE_COUNT_TO_PLOT)
		#global particle2p5
		#particle2p5 = airlift.add_most_recent_data_to_end_of_array(particle2p5, "garage-2p5")
		#myarray_d = display_adafruit.format_for_plot(particle2p5, MIN_PARTICLE_COUNT_TO_PLOT, MAX_PARTICLE_COUNT_TO_PLOT)
		#global particle5p0
		#particle5p0 = airlift.add_most_recent_data_to_end_of_array(particle5p0, "garage-5p0")
		#myarray_e = display_adafruit.format_for_plot(particle5p0, MIN_PARTICLE_COUNT_TO_PLOT, MAX_PARTICLE_COUNT_TO_PLOT)
		#global printer0p3
		#printer0p3 = airlift.add_most_recent_data_to_end_of_array(printer0p3, "3d-printer-0p3")
		#myarray_f = display_adafruit.format_for_plot(printer0p3, MIN_PARTICLE_COUNT_TO_PLOT, MAX_PARTICLE_COUNT_TO_PLOT)
		#global printer0p5
		#printer0p5 = airlift.add_most_recent_data_to_end_of_array(printer0p5, "3d-printer-0p5")
		#myarray_g = display_adafruit.format_for_plot(printer0p5, MIN_PARTICLE_COUNT_TO_PLOT, MAX_PARTICLE_COUNT_TO_PLOT)
		global printer1p0
		printer1p0 = airlift.add_most_recent_data_to_end_of_array(printer1p0, "3d-printer-1p0")
		myarray_h = display_adafruit.format_for_plot(printer1p0, MIN_PARTICLE_COUNT_TO_PLOT, MAX_PARTICLE_COUNT_TO_PLOT)
		#global printer2p5
		#printer2p5 = airlift.add_most_recent_data_to_end_of_array(printer2p5, "3d-printer-2p5")
		#myarray_i = display_adafruit.format_for_plot(printer2p5, MIN_PARTICLE_COUNT_TO_PLOT, MAX_PARTICLE_COUNT_TO_PLOT)
		#global printer5p0
		#printer5p0 = airlift.add_most_recent_data_to_end_of_array(printer5p0, "3d-printer-5p0")
		#myarray_j = display_adafruit.format_for_plot(printer5p0, MIN_PARTICLE_COUNT_TO_PLOT, MAX_PARTICLE_COUNT_TO_PLOT)
		display_adafruit.update_plot(3, [myarray_c, myarray_h])
	display_adafruit.refresh()
	flush()
	generic.collect_garbage(True)
	#gc.collect()
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
	generic.collect_garbage(True)
	global sdcard_is_available
	sdcard_is_available = False
	global dirname
	if should_use_sdcard:
		sdcard_is_available = microsd_adafruit.setup_sdcard_for_logging_data(spi, board.SD_CS, dirname)
	else:
		dirname = ""
	if sdcard_is_available:
		if RTC_is_available:
			create_new_logfile_with_string_embedded(dirname, "weather_station", pcf8523_adafruit.get_timestring2())
		else:
			create_new_logfile_with_string_embedded(dirname, "weather_station")
	generic.collect_garbage(True)
	display_adafruit.setup_for_n_m_plots(2, 2, [["temperature", "living-room", "3d-printer", "outdoor", "roof", "heater"], ["humidity", "living-room", "3d-printer", "outdoor", "roof"], ["pressure", "living-room", "3d-printer"], ["particle count", "garage-1.0", "3d-printer-1.0"]])
	display_adafruit.refresh()
	array_size = display_adafruit.plot_width
	if 1:
		#gc.collect()
		generic.collect_garbage(True)
		global temperature_indoor
		temperature_indoor = [ -40.0 for i in range(array_size) ]
		global temperature_3dprinter
		temperature_3dprinter= [ -40.0 for i in range(array_size) ]
		global temperature_outdoor
		temperature_outdoor = [ -40.0 for i in range(array_size) ]
		global ds18b20
		ds18b20 = [ -40.0 for i in range(array_size) ]
		global heater
		heater = [ -40.0 for i in range(array_size) ]
		global humidity_living_room
		humidity_living_room = [ -40.0 for i in range(array_size) ]
		global humidity_indoor
		humidity_indoor = [ -40.0 for i in range(array_size) ]
		global humidity_outdoor
		humidity_outdoor = [ -40.0 for i in range(array_size) ]
		global sht31d
		sht31d = [ -40.0 for i in range(array_size) ]
		global pressure_living_room
		pressure_living_room = [ -40.0 for i in range(array_size) ]
		global pressure
		pressure = [ -40.0 for i in range(array_size) ]
		#global particle0p3
		#particle0p3 = [ -40.0 for i in range(array_size) ]
		#global particle0p5
		#particle0p5 = [ -40.0 for i in range(array_size) ]
		global particle1p0
		particle1p0 = [ -40.0 for i in range(array_size) ]
		#global particle2p5
		#particle2p5 = [ -40.0 for i in range(array_size) ]
		#global particle5p0
		#particle5p0 = [ -40.0 for i in range(array_size) ]
		#global printer0p3
		#printer0p3 = [ -40.0 for i in range(array_size) ]
		#global printer0p5
		#printer0p5 = [ -40.0 for i in range(array_size) ]
		global printer1p0
		printer1p0 = [ -40.0 for i in range(array_size) ]
		#global printer2p5
		#printer2p5 = [ -40.0 for i in range(array_size) ]
		#global printer5p0
		#printer5p0 = [ -40.0 for i in range(array_size) ]
		#gc.collect()
	if 0:
		print("fetching old data from feeds...")
		#global temperature_indoor
		#temperature_indoor = airlift.get_all_data("inside-temp", array_size)
		global humidity_indoor
		humidity_indoor = airlift.get_all_data("inside-hum", array_size)
		print(str(humidity_indoor))
	generic.collect_garbage(True)
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

