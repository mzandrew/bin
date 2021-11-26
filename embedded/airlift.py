#!/usr/bin/env python3

# written 2021-05-01 by mza
# last updated 2021-11-26 by mza

#from adafruit_esp32spi import adafruit_esp32spi_wifimanager

import time
import board
import busio
import digitalio
from adafruit_esp32spi import adafruit_esp32spi
from adafruit_esp32spi import PWMOut
from adafruit_io.adafruit_io import IO_HTTP, AdafruitIO_RequestError
import adafruit_requests as requests
import adafruit_esp32spi.adafruit_esp32spi_socket as socket
import pcf8523_adafruit # to set the RTC
import math
from DebugInfoWarningError24 import debug, info, warning, error, debug2, debug3, set_verbosity, create_new_logfile_with_string_embedded, flush

epsilon = 0.000001
MAXERRORCOUNT = 5
errorcount = 0
myfeeds = []
delay = 0.25

#spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
def setup_airlift(spi, number_of_retries_remaining=5):
	global saved_spi
	saved_spi = spi
	global esp
	global socket
	global requests
	global io
	if 2==number_of_retries_remaining:
		esp.reset()
	if 0==number_of_retries_remaining:
		error("can't initialize airlift wifi")
		return False
	# from https://github.com/ladyada/Adafruit_CircuitPython_ESP32SPI/blob/master/examples/esp32spi_localtime.py
	# and https://learn.adafruit.com/adafruit-airlift-featherwing-esp32-wifi-co-processor-featherwing?view=all
	# and https://learn.adafruit.com/adafruit-io-basics-airlift/circuitpython
	# and https://github.com/adafruit/Adafruit_CircuitPython_ESP32SPI/blob/main/adafruit_esp32spi/adafruit_esp32spi.py
	global secrets
	try:
		from secrets import secrets
	except ImportError:
		warning("WiFi secrets are kept in secrets.py, please add them there!")
		return False
	try:
		esp32_cs = digitalio.DigitalInOut(board.D13)
		esp32_ready = digitalio.DigitalInOut(board.D11)
		esp32_reset = digitalio.DigitalInOut(board.D12)
		esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)
		#if esp.status == adafruit_esp32spi.WL_IDLE_STATUS:
			#info("ESP32 found and in idle mode")
			#print("Firmware vers.", esp.firmware_version)
			#print("MAC addr:", [hex(i) for i in esp.MAC_address])
		#for ap in esp.scan_networks():
		#	print("\t%s\t\tRSSI: %d" % (str(ap['ssid'], 'utf-8'), ap['rssi']))
		info("Connecting to " + secrets["ssid"] + "...")
		while not esp.is_connected:
			try:
				esp.connect_AP(secrets["ssid"], secrets["password"])
			except RuntimeError as e:
				info("could not connect to AP, retrying: " + str(e))
				continue
		#info("Connected to", str(esp.ssid, 'utf-8'), "\tRSSI:", esp.rssi)
		info("My IP address is " + esp.pretty_ip(esp.ip_address))
		socket.set_interface(esp)
		requests.set_socket(socket, esp)
		io = IO_HTTP(secrets["aio_username"], secrets["aio_key"], requests)
		info("RSSI: " + str(esp.rssi) + " dB") # receiving signal strength indicator
		#info("IP lookup adafruit.com: %s" % esp.pretty_ip(esp.get_host_by_name("adafruit.com")))
		#info("Ping google.com: %d ms" % esp.ping("google.com"))
		#requests.set_socket(socket, esp)
		#TEXT_URL = "http://wifitest.adafruit.com/testwifi/index.html"
		#info("Fetching text from " + TEXT_URL)
		#r = requests.get(TEXT_URL)
		#print("-" * 40)
		#info(r.text)
		#print("-" * 40)
		#r.close()
		#from adafruit_esp32spi import PWMOut
#		try:
#			import adafruit_rgbled
#		except:
#			error("you need adafruit_rgbled.mpy and/or simpleio.mpy")
#			raise
		#RED_LED = PWMOut.PWMOut(esp, 26)
		#GREEN_LED = PWMOut.PWMOut(esp, 25)
		#BLUE_LED = PWMOut.PWMOut(esp, 27)
		#status_light = adafruit_rgbled.RGBLED(RED_LED, BLUE_LED, GREEN_LED)
		#wifi = adafruit_esp32spi_wifimanager.ESPSPI_WiFiManager(esp, secrets, status_light)
		#DATA_SOURCE = "https://www.google.com/index.html"
		#try:
		#	response = wifi.get(DATA_SOURCE)
		#except:
		#	wifi.reset()
	except:
		time.sleep(delay)
		setup_airlift(spi, number_of_retries_remaining-1)
	return True

def setup_feed(feed_name, number_of_retries_remaining=5):
	global myfeeds
	for feed in myfeeds:
		if feed_name==feed[0]:
			return feed[1]
	if 0==number_of_retries_remaining:
		#esp.reset()
		return False
	try:
		info("connecting to feed " + feed_name + "...")
		try:
			myfeed = io.get_feed(feed_name)
		except AdafruitIO_RequestError:
			info("creating new feed " + feed_name + "...")
			myfeed = io.create_new_feed(feed_name)
	except:
		time.sleep(delay)
		myfeed = setup_feed(feed_name, number_of_retries_remaining-1)
	myfeeds.append([ feed_name , myfeed ])
	return myfeed

def post_data(feed_name, value, perform_readback_and_verify=False):
	global errorcount
	myfeed = setup_feed(feed_name)
	try:
		value = float(value)
		info("publishing " + str(value))
		for i in range(5):
			try:
				io.send_data(myfeed["key"], value) # sometimes this gives RuntimeError: Sending request failed
				break
			except:
				if 0==i:
					raise
				else:
					time.sleep(delay)
		#info("done")
		if perform_readback_and_verify:
			received_data = io.receive_data(myfeed["key"])
			readback = float(received_data["value"])
			if epsilon<math.fabs(readback-value):
				errorcount = 0
			else:
				errorcount += 1
				warning("readback failure " + str(readback) + "!=" + str(value))
	except:
		errorcount += 1
		error("couldn't publish data (" + str(errorcount) + "/" + str(MAXERRORCOUNT) + ")")
	if MAXERRORCOUNT<errorcount:
		esp.reset()
		setup_airlift(saved_spi)

#def get_previous():
#	try:
#		value = io.receive_previous(myfeed["key"]) # the circuitpython library can't do this
#	except:
#		raise
#	return value

DEFAULT = -40
def get_all_data(count):
	# this function is still under construction...
	try:
		reverse_order_values = io.receive_all_data(myfeed["key"]) # out of memory
		if count<len(reverse_order_values):
			reverse_order_values = reverse_order_values[:count]
		if len(reverse_order_values)<count:
			for i in range(len(reverse_order_values), count):
				reverse_order_values.append(DEFAULT)
		for i in range(count):
			values[i] = reverse_order_values[count - i]
		return values
	except:
		raise

def old_post_data(data):
	try:
		#feed = "heater"
		feed = "test"
		payload = {"value": data}
		url = "https://io.adafruit.com/api/v2/" + secrets["aio_username"] + "/feeds/" + feed + "/data"
		response = wifi.post(url, json=payload, headers={"X-AIO-KEY": secrets["aio_key"]})
		#info(response.json())
		response.close()
	except:
		error("couldn't perform POST operation")

def update_time_from_server():
	info("setting RTC time from server...")
	try:
		time = io.receive_time()
		#info(str(time))
	except:
		warning("couldn't get time from server")
	try:
		pcf8523_adafruit.set_from_timestruct(time)
	except:
		warning("couldn't set RTC")

