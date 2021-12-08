#!/usr/bin/env python3

# written 2021-05-01 by mza
# last updated 2021-12-08 by mza

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
delay = 1.0
DESIRED_PRECISION_DEGREES = 7
DESIRED_PRECISION_METERS = 3

def hex(number, width=1):
	return "%0*x" % (width, number)

def format_MAC(MAC):
	string = ""
	for byte in MAC:
		if len(string):
			string += "-"
		string += hex(byte, 2)
	return string

def show_networks(networks):
	for network in networks:
		string = ""
		string += format_MAC(network[1])
		string += ", " + str(network[3])
		string += ", " + str(network[2])
		string += ", " + network[0]
		info(string)

def scan_networks():
	networks = []
	for network in wifi.radio.start_scanning_networks():
		ssid = str(network.ssid, "utf-8")
		bssid = list(network.bssid)
		channel = network.channel
		rssi = network.rssi
		networks.append([ssid, bssid, channel, rssi])
	wifi.radio.stop_scanning_networks()
	networks.sort(key=lambda farquar:farquar[3], reverse=True) # sort by signal strength
	return networks

# for esp32-s2 boards
# from https://learn.adafruit.com/adafruit-metro-esp32-s2/circuitpython-internet-test
def setup_wifi():
	global wifi
	global io
	import wifi
	import ipaddress
	import socketpool
	import adafruit_requests
	import ssl
	wifi.radio.hostname = "RoamIfYouWantTo"
	networks = scan_networks()
	show_networks(networks)
	try:
		from secrets import secrets
	except ImportError:
		warning("WiFi secrets are kept in secrets.py, please add them there!")
		return False
	wifi.radio.connect(ssid=secrets["ssid"], password=secrets["password"])
	mac_address = list(wifi.radio.mac_address)
	info("MAC: " + format_MAC(mac_address))
	info("IP: " + str(wifi.radio.ipv4_address))
	info("RSSI: " + str(wifi.radio.ap_info.rssi) + " dB") # receiving signal strength indicator
#	ap_mac = list(wifi.radio.mac_address_ap)
#	info(str(ap_mac))
	pool = socketpool.SocketPool(wifi.radio)
	requests = adafruit_requests.Session(pool, ssl.create_default_context())
	io = IO_HTTP(secrets["aio_username"], secrets["aio_key"], requests)
	#ipv4 = ipaddress.ip_address("8.8.4.4") # google.com
	#info(str(wifi.radio.ping(ipv4)*1000))
	return True

#spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
def setup_airlift(spi, cs_pin, ready_pin, reset_pin, number_of_retries_remaining=5):
	global saved_spi
	saved_spi = spi
	global esp
	#global socket
	#global requests
	global io
	if number_of_retries_remaining<3:
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
		esp32_cs = digitalio.DigitalInOut(cs_pin)
		esp32_ready = digitalio.DigitalInOut(ready_pin)
		esp32_reset = digitalio.DigitalInOut(reset_pin)
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

def show_network_status():
	info("My IP address is " + esp.pretty_ip(esp.ip_address))
	try:
		info("RSSI: " + str(esp.rssi) + " dB") # receiving signal strength indicator
	except:
		info("RSSI: " + str(wifi.radio.ap_info.rssi) + " dB") # receiving signal strength indicator

def setup_feed(feed_name, number_of_retries_remaining=5):
	global myfeeds
	for feed in myfeeds:
		if feed_name==feed[0]:
			return feed[1]
	if 0==number_of_retries_remaining:
		show_network_status()
		#esp.reset()
		return False
	try:
		info("connecting to feed " + feed_name + "...")
		try:
			myfeed = io.get_feed(feed_name)
		except AdafruitIO_RequestError:
			info("creating new feed " + feed_name + "...")
			myfeed = io.create_new_feed(feed_name)
		#info(str(myfeed["key"]))
	except:
		time.sleep(delay)
		myfeed = setup_feed(feed_name, number_of_retries_remaining-1)
	if myfeed:
		myfeeds.append([ feed_name , myfeed ])
	return myfeed

def post_data(feed_name, value, perform_readback_and_verify=False):
	global errorcount
	myfeed = setup_feed(feed_name)
	if not myfeed:
		warning("feed " + feed_name + " not connected")
		return
	try:
		value = float(value)
		info("publishing " + str(value) + " to feed " + feed_name)
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
		else:
			errorcount = 0
	except:
		errorcount += 1
		error("couldn't publish data (" + str(errorcount) + "/" + str(MAXERRORCOUNT) + ")")
		show_network_status()
#	if MAXERRORCOUNT<errorcount:
#		esp.reset()
#		setup_airlift(saved_spi)

def show_geolocation_error(metadata, received_data):
	lat = float(received_data["lat"])
	lon = float(received_data["lon"])
	ele = float(received_data["ele"])
	string = "%.6f,%.6f,%.3f" % (lat, lon, ele)
	info("readback location = " + string)
	err_lat = float(metadata["lat"]) - lat
	err_lon = float(metadata["lon"]) - lon
	#err_ele = metadata["ele"] - ele
	#string += " error(deg) = %.6f,%.6f" % (err_lat, err_lon)
	equatorial_circumference_km = 40075.017
	equatorial_m_per_degree = 1000. * equatorial_circumference_km / 360.
	err_lon_m = err_lon * equatorial_m_per_degree
	meridional_circumference_km = 40007.86
	meridional_m_per_degree = 1000. * meridional_circumference_km / 360.
	err_lat_m = err_lat * meridional_m_per_degree
	string = "location error in readback = %.3f,%.3f (m)" % (err_lat_m, err_lon_m)
	info(string)

# https://github.com/adafruit/Adafruit_CircuitPython_AdafruitIO/blob/main/examples/adafruit_io_http/adafruit_io_metadata.py
def test_posting_geolocated_data(feed_name):
	myfeed = setup_feed(feed_name)
	data_value = 42.000000123456789
	metadata = {"lat": 21.123456, "lon": -157.654321, "ele": -6.283823, "created_at": None} # "123 fake street"
	string = "%.6f,%.6f,%.3f" % (metadata["lat"], metadata["lon"], metadata["ele"])
	info("location = " + string)
	info("value = %.9f" % data_value)
	metadata["lat"] = "%.7f" % metadata["lat"]
	metadata["lon"] = "%.7f" % metadata["lon"]
	metadata["ele"] = "%.4f" % metadata["ele"]
	io.send_data(myfeed["key"], data_value, metadata, precision=9)
	received_data = io.receive_data(myfeed["key"])
	info("readback value = %.9f" % float(received_data["value"]))
	show_geolocation_error(metadata, received_data)

def post_geolocated_data(feed_name, location, value, perform_readback_and_verify=False):
	metadata = {}
	metadata["lat"] = location[0]
	metadata["lon"] = location[1]
	metadata["ele"] = location[2]
	if 0:
		info(str(metadata))
	elif 0:
		string = "location = "
#		for i in range(len(location)):
#			string += ",%.6f" % location[i]
		string += " "
		string += "%.6f" % metadata["lat"]
		string += ",%.6f" % metadata["lon"]
		string += ",%.3f" % metadata["ele"]
		info(string)
	global errorcount
	myfeed = setup_feed(feed_name)
	if not myfeed:
		warning("feed " + feed_name + " not connected")
		return
	metadata["lat"] = "%.*f" % (DESIRED_PRECISION_DEGREES, metadata["lat"])
	metadata["lon"] = "%.*f" % (DESIRED_PRECISION_DEGREES, metadata["lon"])
	metadata["ele"] = "%.*f" % (DESIRED_PRECISION_METERS, metadata["ele"])
	try:
		value = float(value)
		info("publishing " + str(value) + " to feed " + feed_name + " @(" + metadata["lat"] + "," + metadata["lon"] + "," + metadata["ele"]  + ")")
		for i in range(5):
			try:
				io.send_data(myfeed["key"], value, metadata=metadata) # sometimes this gives RuntimeError: Sending request failed
				#io.send_data(myfeed["key"], value, metadata=metadata, precision=6) # sometimes this gives RuntimeError: Sending request failed
				break
			except:
				if 0==i:
					raise
				else:
					time.sleep(delay)
		#perform_readback_and_verify = True
		if perform_readback_and_verify:
			received_data = io.receive_data(myfeed["key"])
			#readback = float(received_data["value"])
			show_geolocation_error(metadata, received_data)
#			if epsilon<math.fabs(readback-value):
#				errorcount = 0
#			else:
#				errorcount += 1
#				warning("readback failure " + str(readback) + "!=" + str(value))
	except:
		errorcount += 1
		error("couldn't publish data (" + str(errorcount) + "/" + str(MAXERRORCOUNT) + ")")

#data_list = [Data(value=10), Data(value=11)]

#def get_previous():
#	try:
#		value = io.receive_previous(myfeed["key"]) # the circuitpython library can't do this
#	except:
#		raise
#	return value

# curl -H "X-AIO-Key: {io_key}" "https://io.adafruit.com/api/v2/{username}/feeds/{feed_key}/data?limit=1&end_time=2019-05-05T00:00Z"
# curl -H "X-AIO-Key: {io_key}" "https://io.adafruit.com/api/v2/{username}/feeds/{feed_key}/data?start_time=2019-05-04T00:00Z&end_time=2019-05-05T00:00Z"
# Not implemented in Adafruit IO CircuitPython
def get_some_data(feed_key, start_time, end_time, limit=1):
	adafruit_io.validate_feed_key(feed_key)
	path = adafruit_io._compose_path("feeds/{0}/data?start_time={0}&end_time={0}&limit={0}".format(feed_key, start_time, end_time, limit))
	return adafruit_io._get(path)

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

def show_signal_strength():
	try:
		info("RSSI: " + str(esp.rssi) + " dB") # receiving signal strength indicator
	except:
		info("RSSI: " + str(wifi.radio.ap_info.rssi) + " dB") # receiving signal strength indicator

def get_values():
	try:
		values = [ esp.rssi ]
	except:
		try:
			values = [ wifi.radio.ap_info.rssi ]
		except:
			values = [ 0. ]
	return values

def measure_string():
	values = get_values()
	return ", " + str(values[0])

