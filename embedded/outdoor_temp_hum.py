# written 2022-01-12 by mza
# based on solar_water_heater.py
# last updated 2022-01-12 by mza

# to install on a circuitpython device:
# rsync -av *.py /media/circuitpython/
# cp -a outdoor_temp_hum.py /media/circuitpython/code.py
# cd ~/build/adafruit-circuitpython/bundle/lib
# rsync -r simpleio.mpy adafruit_esp32spi adafruit_register adafruit_sdcard.mpy neopixel.mpy adafruit_onewire adafruit_gps.mpy adafruit_sht31d.mpy adafruit_io adafruit_requests.mpy /media/circuitpython/lib/

header_string = "date/time"
mydir = "/logs"
should_use_airlift = True
if 0: # for the one with the TFT and GPS but no adalogger
	FEATHER_ESP32S2 = True
	use_pwm_status_leds = False
	should_use_sdcard = False
	should_use_RTC = False
	should_use_gps = True
	N = 8
	gps_delay_in_ms = 1000
	delay_between_acquisitions = 2. * gps_delay_in_ms/1000.
	delay_between_posting_and_next_acquisition = 2.0
	use_built_in_wifi = True
elif 0: # cat on a hot tin roof
	FEATHER_ESP32S2 = False
	use_pwm_status_leds = True
	should_use_sdcard = True
	should_use_RTC = True
	should_use_gps = False
	N = 32
	delay_between_acquisitions = 0.75
	gps_delay_in_ms = 2000
	delay_between_posting_and_next_acquisition = 4.0
	use_built_in_wifi = False
else: # outdoor temp/hum
	FEATHER_ESP32S2 = False
	use_pwm_status_leds = False
	should_use_sdcard = False
	should_use_RTC = False
	should_use_gps = False
	N = 32
	delay_between_acquisitions = 1.55
	gps_delay_in_ms = 2000
	delay_between_posting_and_next_acquisition = 1.0
	use_built_in_wifi = True

import sys
import time
import atexit
import supervisor
import board
import busio
import pwmio
import simpleio
from adafruit_onewire.bus import OneWireBus
import microsd_adafruit
import neopixel_adafruit
import sht31d_adafruit
import airlift
import gps_adafruit
from DebugInfoWarningError24 import debug, info, warning, error, debug2, debug3, set_verbosity, create_new_logfile_with_string_embedded, flush
import generic

# https://learn.adafruit.com/circuitpython-essentials/circuitpython-pwm
PWM_MAX = 65535
def setup_status_leds(red_pin, green_pin, blue_pin):
	global status_led
	status_led = []
	status_led.append(pwmio.PWMOut(red_pin,   frequency=5000, duty_cycle=PWM_MAX))
	status_led.append(pwmio.PWMOut(green_pin, frequency=5000, duty_cycle=PWM_MAX))
	status_led.append(pwmio.PWMOut(blue_pin,  frequency=5000, duty_cycle=PWM_MAX))

def set_status_led_color(desired_color):
	global status_led
	for i in range(3):
		duty_cycle = int(PWM_MAX - 1.0*PWM_MAX*desired_color[i])
		if duty_cycle<0:
			duty_cycle = 0
		if PWM_MAX<duty_cycle:
			duty_cycle = PWM_MAX
		status_led[i].duty_cycle = duty_cycle

def print_compact(string):
	date = ""
	if ""==date:
		try:
			date = time.strftime("%Y-%m-%d+%X")
		except:
			pass
	if ""==date and RTC_is_available:
		try:
			date = pcf8523_adafruit.get_timestring1()
		except:
			pass
	if ""==date and gps_is_available:
		try:
			date = gps_adafruit.get_time()
		except:
			pass
	info("%s%s" % (date, string))

def print_header():
	info("" + header_string)

def main():
	global header_string
	if use_pwm_status_leds:
		setup_status_leds(red_pin=board.A2, green_pin=board.D9, blue_pin=board.A3)
		set_status_led_color([1.0, 1.0, 1.0])
	if FEATHER_ESP32S2: # for feather esp32-s2 to turn on power to i2c bus:
		simpleio.DigitalOut(board.D7, value=0)
	global i2c
	try:
		i2c = busio.I2C(board.SCL1, board.SDA1)
		string = "using I2C1 "
	except:
		#i2c = busio.I2C(board.SCL, board.SDA)
		i2c = board.I2C()
		string = "using I2C0 "
	info(string)
	#i2c.try_lock()
	#i2c_list = i2c.scan()
	#i2c.unlock()
	#info(string + str(i2c_list))
	global spi
	spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
	global uart
	uart = busio.UART(board.TX, board.RX, baudrate=9600, timeout=10)
	prohibited_addresses = []
	global RTC_is_available
	if should_use_RTC:
		try:
			i2c_address = pcf8523_adafruit.setup(i2c)
			prohibited_addresses.append(i2c_address)
			RTC_is_available = True
		except:
			RTC_is_available = False
	else:
		RTC_is_available = False
	global sdcard_is_available
	global mydir
	if should_use_sdcard:
		sdcard_is_available = microsd_adafruit.setup_sdcard_for_logging_data(spi, board.D10, mydir) # D10 = adalogger featherwing
	else:
		sdcard_is_available = False
	if not sdcard_is_available:
		mydir = "/"
	if RTC_is_available:
		create_new_logfile_with_string_embedded(mydir, "solar_water_heater", pcf8523_adafruit.get_timestring2())
	else:
		create_new_logfile_with_string_embedded(mydir, "solar_water_heater")
	global gps_is_available
	if should_use_gps:
		if 1:
			gps_adafruit.setup_uart(uart, N, gps_delay_in_ms)
		else:
			gps_adafruit.setup_i2c(i2c, N, gps_delay_in_ms)
		gps_is_available = True
		header_string += gps_adafruit.header_string()
	else:
		gps_is_available = False
	global neopixel_is_available
	try:
		neopixel_is_available = neopixel_adafruit.setup_neopixel()
	except:
		warning("error setting up neopixel")
	global sht31d_is_available
	try:
		i2c_address = sht31d_adafruit.setup(i2c, N)
		prohibited_addresses.append(i2c_address)
		header_string += ", sht31d-%RH, sht31d-C"
		sht31d_is_available = True
	except:
		error("sht31d not found")
		sys.exit(1)
		sht31d_is_available = False
	#info("prohibited i2c addresses: " + str(prohibited_addresses)) # disallow treating any devices already discovered as pct2075s
	if use_pwm_status_leds:
		set_status_led_color([0.5, 0.5, 0.5])
	global airlift_is_available
	if should_use_airlift:
		if use_built_in_wifi:
			airlift_is_available = airlift.setup_wifi("outdoor-temp-hum")
		else:
			airlift_is_available = airlift.setup_airlift("outdoor-temp-hum", spi, board.D13, board.D11, board.D12)
		header_string += ", RSSI-dB"
	else:
		airlift_is_available = False
	if 0:
		if airlift_is_available:
			airlift.update_time_from_server()
	#gnuplot> set key autotitle columnheader
	#gnuplot> set style data lines
	#gnuplot> plot for [i=1:14] "solar_water_heater.log" using 0:i
	print_header()
	global i
	i = 0
	loop()
	info("sht31d no longer available; cannot continue")

def loop():
	global i
	while sht31d_adafruit.test_if_present():
		neopixel_adafruit.set_color(255, 0, 0)
		if use_pwm_status_leds:
			set_status_led_color([1, 0, 0])
		string = ""
		if gps_is_available:
			string += gps_adafruit.measure_string()
		if sht31d_is_available:
			#info("sht31d")
			string += sht31d_adafruit.measure_string()
		if airlift_is_available:
			string += airlift.measure_string()
		print_compact(string)
		flush()
		neopixel_adafruit.set_color(0, 255, 0)
		if use_pwm_status_leds:
			set_status_led_color([0, 1, 0])
		i += 1
		if 0==i%N:
			if sht31d_is_available:
				sht31d_adafruit.show_average_values()
				if airlift_is_available:
					try:
						airlift.post_data("outdoor-temp", sht31d_adafruit.get_average_values()[1])
						airlift.post_data("outdoor-hum", sht31d_adafruit.get_average_values()[0])
					except:
						warning("couldn't post data for sht31d")
			info("waiting...")
			time.sleep(delay_between_posting_and_next_acquisition)
		neopixel_adafruit.set_color(0, 0, 255)
		if use_pwm_status_leds:
			set_status_led_color([0, 0, 1])
		if airlift_is_available:
			if 0==i%86300:
				airlift.update_time_from_server()
		time.sleep(delay_between_acquisitions)

if __name__ == "__main__":
	#supervisor.disable_autoreload()
	atexit.register(generic.reset)
	try:
		main()
	except KeyboardInterrupt:
		info("caught ctrl-c")
		flush()
		atexit.unregister(generic.reset)
		sys.exit(0)
	except ReloadException:
		info("reload exception")
		flush()
		atexit.unregister(generic.reset)
		time.sleep(1)
		supervisor.reload()
	info("leaving program...")
	flush()
	generic.reset()

