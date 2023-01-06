#!/usr/bin/env python3

# written 2021-05-01 by mza
# last updated 2022-12-02 by mza

import time
import busio
import digitalio
import math
import boxcar
import generic
from DebugInfoWarningError24 import debug, info, warning, error, debug2, debug3, set_verbosity, create_new_logfile_with_string_embedded, flush

VALUE_INDEX = 3 # gotta know that "value" is index #3 in the tuple

secrets_already_imported = False
def import_secrets_if_necessary():
	global secrets_already_imported
	global secrets
	if secrets_already_imported:
		return
	try:
		from secrets import secrets
		secrets_already_imported = True
	except (KeyboardInterrupt, ReloadException):
		raise
	except ImportError:
		warning("WiFi secrets are kept in secrets.py, please add them there!")

epsilon = 0.000001
MAXERRORCOUNT = 5
SUPERMAXERRORCOUNT = 10
errorcount = 0
myfeeds = []
mydesiredfeeds = []
DELAY = 1.0
DESIRED_PRECISION_DEGREES = 7
DESIRED_PRECISION_METERS = 3
DEFAULT_VALUE = -40
mydesiredhostname = "samwise"
airlift_pins_already_setup = False
esp_already_setup = False
myboxcar_already_setup = False

def format_MAC(MAC):
	string = ""
	for byte in MAC:
		if len(string):
			string += "-"
		string += generic.hex(byte, 2)
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
	import wifi # needed to call static methods
	for network in wifi.radio.start_scanning_networks():
		ssid = str(network.ssid, "utf-8")
		bssid = list(network.bssid)
		channel = network.channel
		rssi = network.rssi
		networks.append([ssid, bssid, channel, rssi])
	wifi.radio.stop_scanning_networks()
	networks.sort(key=lambda farquar:farquar[3], reverse=True) # sort by signal strength
	return networks

def turn_off_wifi():
	show_network_status()
	try:
		if using_builtin_wifi:
			import wifi # needed to call static methods
			wifi.radio.enabled = False
		else:
			esp.disconnect()
	except (KeyboardInterrupt, ReloadException):
		raise
	except Exception as error_message:
		error("can't turn off/disconnect wifi")
		error(str(error_message))
	global myfeeds
	myfeeds = []
	show_network_status()

def turn_on_wifi():
	show_network_status()
	try:
		if using_builtin_wifi:
			import wifi # needed to call static methods
			wifi.radio.enabled = True
			setup_wifi(mydesiredhostname)
		else:
			setup_airlift(mydesiredhostname, None, None, None)
	except (KeyboardInterrupt, ReloadException):
		raise
	except Exception as error_message:
		error("can't turn on/reconnect wifi")
		error(str(error_message))
	try:
		setup_feeds_again()
	except (KeyboardInterrupt, ReloadException):
		raise
	except Exception as error_message:
		error("can't setup feeds again")
		error(str(error_message))
	show_network_status()

def connect_wifi(hostname):
	try:
		import wifi
	except (KeyboardInterrupt, ReloadException):
		raise
	except ImportError:
		print("can't import wifi")
		raise
	try:
		import ssl
	except (KeyboardInterrupt, ReloadException):
		raise
	except ImportError:
		print("can't import ssl")
		raise
	try:
		import socketpool
	except (KeyboardInterrupt, ReloadException):
		raise
	except ImportError:
		print("can't import socketpool")
		raise
	try:
		import adafruit_requests
	except (KeyboardInterrupt, ReloadException):
		raise
	except ImportError:
		print("can't import adafruit_requests")
		raise
	try:
		from adafruit_io.adafruit_io import IO_HTTP
	except (KeyboardInterrupt, ReloadException):
		raise
	except ImportError:
		print("can't import adafruit_io (HTTP)")
		raise
	global io
	if 0:
		try:
			if wifi.radio.enabled:
				wifi.radio.enabled = False
				time.sleep(0.25)
				wifi.radio.enabled = True
				time.sleep(0.25)
		except (KeyboardInterrupt, ReloadException):
			raise
		except Exception as error_message:
			pass
	import_secrets_if_necessary()
	try:
		info("Connecting to " + secrets["ssid"] + "...")
		try:
			wifi.radio.hostname = hostname
		except (KeyboardInterrupt, ReloadException):
			raise
		except Exception as error_message:
			warning("couldn't set hostname")
			error(str(error_message))
		#wifi.radio.mac_address = bytes((0x7E, 0xDF, 0xA1, 0xFF, 0xFF, 0xFF))
		#networks = scan_networks()
		#show_networks(networks)
		try:
			wifi.radio.connect(ssid=secrets["ssid"], password=secrets["password"])
		except (KeyboardInterrupt, ReloadException):
			raise
		except Exception as message:
			error("couldn't connect: " + message)
			raise
		show_network_status()
#		ap_mac = list(wifi.radio.mac_address_ap)
#		info(str(ap_mac))
		try:
			pool = socketpool.SocketPool(wifi.radio)
			debug("successfully set up pool")
		except (KeyboardInterrupt, ReloadException):
			raise
		except Exception as message:
			error("couldn't setup socket: " + message)
			raise
		try:
			requests = adafruit_requests.Session(pool, ssl.create_default_context())
			debug("successfully set up requests")
		except (KeyboardInterrupt, ReloadException):
			raise
		except Exception as message:
			error("couldn't setup requests: " + message)
			raise
		try:
			io = IO_HTTP(secrets["aio_username"], secrets["aio_key"], requests)
			debug("successfully set up aio")
		except (KeyboardInterrupt, ReloadException):
			raise
		except Exception as message:
			error("couldn't setup aio: " + message)
			raise
		return True
	except (KeyboardInterrupt, ReloadException):
		raise
	except Exception as error_message:
		#info("could not connect to AP")
		error(str(error_message))
		raise

# for esp32-s2 boards
# from https://learn.adafruit.com/adafruit-metro-esp32-s2/circuitpython-internet-test
def setup_wifi(hostname, number_of_retries_remaining=2):
	global mydesiredhostname
	global myboxcar
	global using_builtin_wifi
	global myboxcar_already_setup
	mydesiredhostname = hostname 
	if not myboxcar_already_setup:
		N = 10
		myboxcar = boxcar.boxcar(1, N, "wifi")
		myboxcar_already_setup = True
	using_builtin_wifi = True
	for i in range(number_of_retries_remaining):
		try:
			if connect_wifi(hostname):
				#show_network_status()
				return True
		except (KeyboardInterrupt, ReloadException):
			raise
		except Exception as error_message:
			error(str(error_message))
			if i<number_of_retries_remaining-1:
				info("")
				info("trying wifi connection again...")
				time.sleep(DELAY)
	error("can't initialize built-in wifi")
	info("")
	#show_network_status()
	return False

# this function does not work:
# from https://issueexplorer.com/issue/adafruit/Adafruit_CircuitPython_ESP32SPI/140
def set_hostname(esp, hostname):
	_SET_HOSTNAME = const(0x16)
	"""Tells the ESP32 to set hostname"""
	print("setting hostname...")
	resp = esp._send_command_get_response(_SET_HOSTNAME, [hostname])
	print(str(resp))
	if resp[0][0] != 1:
		raise RuntimeError("Failed to set hostname with esp32")
	return resp

def esp32_connect(number_of_retries_remaining=2):
	import adafruit_esp32spi.adafruit_esp32spi_socket as socket
	import adafruit_requests
	from adafruit_io.adafruit_io import IO_HTTP
	if number_of_retries_remaining<1:
		return False
	global io
	if esp.is_connected:
		info("already connected")
		show_network_status()
		try:
			esp.disconnect()
			info("disconnected")
		except (KeyboardInterrupt, ReloadException):
			raise
		except Exception as error_message:
			error(str(error_message))
			warning("can't disconnect")
		show_network_status()
	import_secrets_if_necessary()
	while not esp.is_connected:
		info("Connecting to " + secrets["ssid"] + "...")
		try:
			esp.connect_AP(secrets["ssid"], secrets["password"])
		except (KeyboardInterrupt, ReloadException):
			raise
		except RuntimeError as e:
			info("could not connect to AP: " + str(e))
			number_of_retries_remaining -= 1
			if 0==number_of_retries_remaining:
				return False
			else:
				time.sleep(DELAY)
				continue
	#info("Connected to", str(esp.ssid, 'utf-8'), "\tRSSI:", esp.rssi)
	try:
		socket.set_interface(esp)
		debug("successfully set up socket")
	except (KeyboardInterrupt, ReloadException):
		raise
	except Exception as error_message:
		error(str(error_message))
		error("couln't set up socket")
		show_network_status()
		return False
	try:
		adafruit_requests.set_socket(socket, esp)
		debug("successfully set up requests")
	except (KeyboardInterrupt, ReloadException):
		raise
	except Exception as error_message:
		error(str(error_message))
		error("couln't set up requests")
		show_network_status()
		return False
	try:
		io = IO_HTTP(secrets["aio_username"], secrets["aio_key"], adafruit_requests)
		debug("successfully set up aio (HTTP)")
	except (KeyboardInterrupt, ReloadException):
		raise
	except Exception as error_message:
		error(str(error_message))
		error("couln't set up aio")
		show_network_status()
		return False
	show_network_status()
	return True

	# from https://github.com/ladyada/Adafruit_CircuitPython_ESP32SPI/blob/master/examples/esp32spi_localtime.py
	# and https://learn.adafruit.com/adafruit-airlift-featherwing-esp32-wifi-co-processor-featherwing?view=all
	# and https://learn.adafruit.com/adafruit-io-basics-airlift/circuitpython
	# and https://github.com/adafruit/Adafruit_CircuitPython_ESP32SPI/blob/main/adafruit_esp32spi/adafruit_esp32spi.py
#spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
def setup_airlift(hostname, spi, cs_pin, ready_pin, reset_pin, number_of_retries_remaining=2):
	global mydesiredhostname
	global myboxcar
	global esp
	global using_builtin_wifi
	global airlift_pins_already_setup
	global esp_already_setup
	global myboxcar_already_setup
	mydesiredhostname = hostname
	if not myboxcar_already_setup:
		N = 10
		myboxcar = boxcar.boxcar(1, N, "wifi")
		myboxcar_already_setup = True
	#from adafruit_esp32spi import PWMOut
	from adafruit_esp32spi import adafruit_esp32spi
	using_builtin_wifi = False
	if not airlift_pins_already_setup:
		try:
			esp32_cs = digitalio.DigitalInOut(cs_pin)
			esp32_ready = digitalio.DigitalInOut(ready_pin)
			esp32_reset = digitalio.DigitalInOut(reset_pin)
			airlift_pins_already_setup = True
		except (KeyboardInterrupt, ReloadException):
			raise
		except Exception as error_message:
			error(str(error_message))
			error("can't set up airlift control pins")
			show_network_status()
			return False
	if not esp_already_setup:
		try:
			esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)
		except (KeyboardInterrupt, ReloadException):
			raise
		except Exception as error_message:
			error(str(error_message))
			error("can't set up esp")
			show_network_status()
			return False
	if 0:
		try:
			set_hostname(esp, hostname)
			#import wifi # needed to call static methods
			#wifi.radio.hostname = hostname
		except (KeyboardInterrupt, ReloadException):
			raise
		except Exception as error_message:
			error(str(error_message))
			warning("can't set hostname")
	for i in range(number_of_retries_remaining):
		try:
			if esp32_connect():
				#show_network_status()
				return True
		except (KeyboardInterrupt, ReloadException):
			raise
		except Exception as error_message:
			error(str(error_message))
			time.sleep(DELAY)
			info("trying wifi connection again...")
	error("can't initialize airlift wifi")
	show_network_status()
	return False

def get_rssi():
	rssi = 0
	if using_builtin_wifi:
		try:
			import wifi # needed to call static methods
			rssi = wifi.radio.ap_info.rssi
		except Exception as error_message:
			error(str(error_message))
			increment_error_count_and_check_error_count_and_reboot_if_too_high()
	else:
		try:
			rssi = esp.rssi
		except Exception as error_message:
			error(str(error_message))
			increment_error_count_and_check_error_count_and_reboot_if_too_high()
	return rssi

def show_network_status():
	try:
		using_builtin_wifi
	except (KeyboardInterrupt, ReloadException):
		raise
	except Exception as error_message:
		error(str(error_message))
		error("wifi is not setup yet (builtin or esp32spi)")
		return
#	try:
#		esp
#		using_builtin_wifi = False
#	except Exception as error_message:
#		pass
#	try:
#		wifi
#		using_builtin_wifi = True
#	except Exception as error_message:
#		pass
	#info("using builtin wifi = " + str(using_builtin_wifi))
	try:
		string = ""
		if using_builtin_wifi:
			import wifi # needed to call static methods
			string += "using internal wifi"
			string += "; MAC: " + format_MAC(list(wifi.radio.mac_address))
			string += "; IP: " + str(wifi.radio.ipv4_address)
			string += "; RSSI: " + str(get_rssi()) + " dB" # receiving signal strength indicator
		else:
			string += "using external/spi wifi"
			string += "; IP: " + esp.pretty_ip(esp.ip_address)
			string += "; RSSI: " + str(get_rssi()) + " dB" # receiving signal strength indicator
			from adafruit_esp32spi import adafruit_esp32spi
			if esp.status == adafruit_esp32spi.WL_IDLE_STATUS:
				string += "; IDLE"
			elif esp.status == adafruit_esp32spi.WL_NO_SSID_AVAIL:
				string += "; NO_SSID_AVAILABLE"
			elif esp.status == adafruit_esp32spi.WL_CONNECTED:
				string += "; CONNECTED"
			elif esp.status == adafruit_esp32spi.WL_CONNECT_FAILED:
				string += "; CONNECT_FAILED"
			elif esp.status == adafruit_esp32spi.WL_CONNECTION_LOST:
				string += "; CONNECTION_LOST"
			elif esp.status == adafruit_esp32spi.WL_DISCONNECTED:
				string += "; DISCONNECTED"
			else:
				string += "; UNKNOWN STATE"
		info(string)
	except (KeyboardInterrupt, ReloadException):
		raise
	except Exception as error_message:
		error(str(error_message))
		increment_error_count_and_check_error_count_and_reboot_if_too_high()

# adafruit io blinka:
# https://learn.adafruit.com/adafruit-io-basics-digital-input/python-setup
# sudo pip3 install --upgrade setuptools
# pip3 install adafruit-blinka
# pip3 install adafruit-io
def setup_io():
	from Adafruit_IO import Client
	global io
	import_secrets_if_necessary()
	try:
		io = Client(secrets["aio_username"], secrets["aio_key"])
	except (KeyboardInterrupt, ReloadException):
		raise
	except Exception as error_message:
		error(str(error_message))
		warning("can't connect to adafruit io")
		increment_error_count_and_check_error_count_and_reboot_if_too_high()

def setup_feed(feed_name, number_of_retries_remaining=2):
	global myfeeds
	for feed in myfeeds: # list of lists, where each entry is: [ feed_name, feed ]
		if feed_name==feed[0]:
			return feed[1]
	debug2("initial len(mydesiredfeeds): " + str(len(mydesiredfeeds)))
	match = False
	for already_added_feed_name in mydesiredfeeds:
		if feed_name == already_added_feed_name:
			match = True
	if not match:
		debug2("adding " + feed_name + " to list of desired feeds")
		mydesiredfeeds.append(feed_name)
	debug2("final len(mydesiredfeeds): " + str(len(mydesiredfeeds)))
	from adafruit_io.adafruit_io import AdafruitIO_RequestError, AdafruitIO_MQTTError, AdafruitIO_ThrottleError
	try:
		io
	except (KeyboardInterrupt, ReloadException):
		raise
	except Exception as error_message:
		error(str(error_message))
		error("can't talk to aio")
		raise
	myfeed = False
	for i in range(number_of_retries_remaining):
		info("attempting to connect to feed " + feed_name + "...")
		try:
			myfeed = io.get_feed(feed_name)
			#myfeed = io.create_and_get_feed(feed_name) # only creates if it isn't already there
			info("connected to feed " + feed_name)
			break
		except (KeyboardInterrupt, ReloadException):
			raise
		except AdafruitIO_RequestError as error_message:
			#error(str(error_message))
			time.sleep(DELAY)
			try:
				myfeed = io.create_new_feed(feed_name)
				info("created new feed " + feed_name)
				break
			except (KeyboardInterrupt, ReloadException):
				raise
			except AdafruitIO_RequestError as error_message:
				error(str(error_message))
			except Exception as error_message:
				error("can't create feed " + feed_name)
				error(str(error_message))
		except AdafruitIO_MQTTError as error_message:
			error("aio MQTT error")
			error(str(error_message))
		except AdafruitIO_ThrottleError as error_message:
			error("aio throttle error")
			error(str(error_message))
		except ValueError as error_message:
			error("invalid feed name: " + feed_name)
			error(str(error_message))
		except RuntimeError as error_message:
			error(str(error_message))
			raise
		except Exception as error_message:
			error("some other problem")
			error(str(error_message))
			show_network_status()
			raise
		#info(str(myfeed["key"]))
		time.sleep(DELAY)
	myfeeds.append([ feed_name , myfeed ])
	return myfeed

def setup_feeds(list_of_feeds, interstitial_delay=0.1):
	info("attempting to set up feeds: " + str(list_of_feeds))
	for feed_name in list_of_feeds:
		setup_feed(feed_name)
		time.sleep(interstitial_delay)
		debug2("successfully set up feed " + feed_name)
	info("successfully set up feeds: " + str(list_of_feeds))

def setup_feeds_again():
	global myfeeds
	myfeeds = []
	info("attempting to set up all feeds again...")
	for feed_name in mydesiredfeeds:
		setup_feed(feed_name)
		debug2("successfully set up feed " + feed_name + " again")
	info("successfully set up all feeds again")

def post_data(feed_name, value, perform_readback_and_verify=False):
	global errorcount
	#debug("attempting to connect to feed " + feed_name + "...")
	myfeed = setup_feed(feed_name)
	if not myfeed:
		warning("feed " + feed_name + " not connected")
		return False
	#debug("attempting to post value " + str(value))
	try:
		value = float(value)
		info("publishing " + str(value) + " to feed " + feed_name)
		for i in range(5):
			try:
				io.send_data(myfeed["key"], value) # sometimes this gives RuntimeError: Sending request failed
				break
			except (KeyboardInterrupt, ReloadException):
				raise
			except Exception as error_message:
				error(str(error_message))
				if 0==i:
					raise
				else:
					time.sleep(DELAY)
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
	except (KeyboardInterrupt, ReloadException):
		raise
	except Exception as error_message:
		error(str(error_message))
		errorcount += 1
		error("couldn't publish data (" + str(errorcount) + "/" + str(MAXERRORCOUNT) + ")")
		show_network_status()
#	if MAXERRORCOUNT<errorcount:
#		info("Attempting reconnection...")
#		try:
#			if using_builtin_wifi:
#				if connect_wifi(hostname):
#					errorcount = 0
#			else:
#				if esp32_connect():
#					errorcount = 0
#		except Exception as error_message:
#			pass
	check_error_count_and_reboot_if_too_high()

def increment_error_count_and_check_error_count_and_reboot_if_too_high():
	global errorcount
	errorcount += 1
	check_error_count_and_reboot_if_too_high()

def check_error_count_and_reboot_if_too_high():
	if SUPERMAXERRORCOUNT<errorcount:
		error("too many errors (" + str(errorcount) + "/" + str(SUPERMAXERRORCOUNT) + ")")
		flush()
		time.sleep(2)
		import generic
		generic.reset()

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
			except (KeyboardInterrupt, ReloadException):
				raise
			except Exception as error_message:
				error(str(error_message))
				if 0==i:
					raise
				else:
					time.sleep(DELAY)
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
		else:
			errorcount = 0
	except (KeyboardInterrupt, ReloadException):
		raise
	except Exception as error_message:
		error(str(error_message))
		errorcount += 1
		error("couldn't publish data (" + str(errorcount) + "/" + str(MAXERRORCOUNT) + ")")
	check_error_count_and_reboot_if_too_high()

def get_most_recent_data(feed):
	global errorcount
	try:
		if generic.running_circuitpython():
			value = io.receive_data(feed)["value"]
		else:
			value = io.receive(feed)[VALUE_INDEX]
		#print(str(value))
		value = float(value)
		#print(str(value))
		errorcount = 0
		return value
	except (KeyboardInterrupt, ReloadException):
		raise
	except Exception as error_message:
		error(str(error_message))
		warning("couldn't get the most recent datapoint for feed " + feed)
		errorcount += 1
	check_error_count_and_reboot_if_too_high()
	return DEFAULT_VALUE

def add_most_recent_data_to_end_of_array(values, feed):
	global errorcount
	try:
		new_value = get_most_recent_data(feed)
		values.append(new_value)
		values.pop(0)
		errorcount = 0
	except (KeyboardInterrupt, ReloadException):
		raise
	except Exception as error_message:
		error(str(error_message))
		warning("couldn't get the most recent datapoint for feed " + feed)
		errorcount += 1
		values.append(DEFAULT_VALUE)
		values.pop(0)
	check_error_count_and_reboot_if_too_high()
	return values

#data_list = [Data(value=10), Data(value=11)]

#def get_previous():
#	try:
#		value = io.receive_previous(myfeed["key"]) # the circuitpython library can't do this
#	except Exception as error_message:
#		raise
#	return value

# curl -H "X-AIO-Key: {io_key}" "https://io.adafruit.com/api/v2/{username}/feeds/{feed_key}/data?limit=1&end_time=2019-05-05T00:00Z"
# curl -H "X-AIO-Key: {io_key}" "https://io.adafruit.com/api/v2/{username}/feeds/{feed_key}/data?start_time=2019-05-04T00:00Z&end_time=2019-05-05T00:00Z"
# Not implemented in Adafruit IO CircuitPython
def get_some_data(feed_key, start_time, end_time, limit=1):
	try:
		adafruit_io.validate_feed_key(feed_key)
		path = adafruit_io._compose_path("feeds/{0}/data?start_time={0}&end_time={0}&limit={0}".format(feed_key, start_time, end_time, limit))
		return adafruit_io._get(path)
	except (KeyboardInterrupt, ReloadException):
		raise
	except Exception as error_message:
		error(str(error_message))
		raise

# url -H "X-AIO-Key: {io_key}" "https://io.adafruit.com/api/v2/{username}/feeds/{feed_key}/data?start_time=2019-05-04T00:00Z&end_time=2019-05-05T00:00Z"
# should use paged mode to get more than 1000 at a time: https://gist.githubusercontent.com/abachman/12df0b34503edd5692be22f6b9695539/raw/5c7faa5fced3f19f14b69424c66b4af6d6d969dd/download_paged_data.py
# in blinka/python, this works
# in circuitpython, we get "AttributeError: 'IO_HTTP' object has no attribute 'data'"
def get_all_data(feed, count_desired=None):
	# fetches 100 if count_desired is None
	global errorcount
	try:
		#info("fetching data from feed " + str(feed) + "...")
		if count_desired is not None:
			raw = io.data(feed, max_results=count_desired)
		else:
			raw = io.data(feed)
		count_gotten = len(raw)
		values = []
		for i in range(count_gotten):
			#values.insert(0, raw[i][VALUE_INDEX])
			values.insert(0, float(raw[i][VALUE_INDEX]))
#		if count_desired is not None:
#			if count_desired<count_gotten:
#				values = values[:count_desired]
#			elif count_gotten<count_desired:
#				for i in range(count_gotten, count_desired):
#					values.append(DEFAULT_VALUE)
		#info("done")
		errorcount = 0
		return values
	except (KeyboardInterrupt, ReloadException):
		raise
	except Exception as error_message:
		error(str(error_message))
		warning("couldn't fetch feed data from server")
		errorcount += 1
		raise
	#check_error_count_and_reboot_if_too_high()

# url -H "X-AIO-Key: {io_key}" "https://io.adafruit.com/api/v2/{username}/feeds/{feed_key}/data?start_time=2019-05-04T00:00Z&end_time=2019-05-05T00:00Z"
# in blinka/python, this works
# in circuitpython, we get "AttributeError: 'IO_HTTP' object has no attribute 'data'"
# format is:
# Data(created_epoch=1651335357, created_at='2022-04-30T16:15:57Z', updated_at=None, value='77.2382', completed_at=None, feed_id=1785141, expiration='2022-06-29T16:15:57Z', position=None, id='0F0K895WA8728HXVYE37EBD27V', lat=None, lon=None, ele=None)
# returns same order as adafruit io csv file downloads
# "id,value,feed_id,created_at,lat,lon,ele" = 8,3,5,1,9,10,11
def get_all_data_with_datestamps(feed, count_desired=None):
	# fetches 100 if count_desired is None
	global errorcount
	DEFAULT_DATESTAMP = "2020-02-02T22:22:22Z"
	DEFAULT_ID = "0F0K8950000000000000000000"
	DEFAULT_LAT = 0.0
	DEFAULT_LON = 0.0
	DEFAULT_ELE = 0.0
	try:
		DATESTAMP_INDEX = 1 # gotta know that "created_at" is index #1 in the tuple
		#info("fetching data from feed " + str(feed) + "...")
		if count_desired is not None:
			raw = io.data(feed, max_results=count_desired)
		else:
			raw = io.data(feed)
		count_gotten = len(raw)
		if count_gotten:
			FEED_ID = raw[0][5]
		values = []
		for i in range(count_gotten):
			#values.insert(0, [raw[i][DATESTAMP_INDEX],raw[i][VALUE_INDEX]])
			#values.insert(0, [ raw[i][8], raw[i][3], raw[i][5], raw[i][1], raw[i][9], raw[i][10], raw[i][11] ])
			values.insert(0, [ raw[i][8], float(raw[i][3]), raw[i][5], raw[i][1], raw[i][9], raw[i][10], raw[i][11] ])
#		if count_desired is not None:
#			if count_desired<count_gotten:
#				values = values[:count_desired]
#			elif count_gotten<count_desired:
#				for i in range(count_gotten, count_desired):
#					values.append([DEFAULT_ID, DEFAULT_VALUE, FEED_ID, DEFAULT_DATESTAMP, DEFAULT_LAT, DEFAULT_LON, DEFAULT_ELE])
		#info("done")
		errorcount = 0
		return values
	except (KeyboardInterrupt, ReloadException):
		raise
	except Exception as error_message:
		error(str(error_message))
		warning("couldn't fetch feed data from server")
		errorcount += 1
		raise
	#check_error_count_and_reboot_if_too_high()

def old_post_data(data):
	import wifi # needed to call static methods
	import_secrets_if_necessary()
	try:
		#feed = "heater"
		feed = "test"
		payload = {"value": data}
		url = "https://io.adafruit.com/api/v2/" + secrets["aio_username"] + "/feeds/" + feed + "/data"
		response = wifi.post(url, json=payload, headers={"X-AIO-KEY": secrets["aio_key"]})
		#info(response.json())
		response.close()
	except (KeyboardInterrupt, ReloadException):
		raise
	except Exception as error_message:
		error(str(error_message))
		error("couldn't perform POST operation")

def get_time_string_from_server():
	global errorcount
	string = ""
	try:
		t = io.receive_time()
		#info(str(t))
		string = "%04d-%02d-%02d+%02d:%02d:%02d" % (t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec)
		errorcount = 0
	except (KeyboardInterrupt, ReloadException):
		raise
	except Exception as error_message:
		error(str(error_message))
		warning("couldn't get time from server")
		errorcount += 1
	check_error_count_and_reboot_if_too_high()
	return string

def update_time_from_server():
	global errorcount
	info("setting RTC time from server...")
	time = ""
	try:
		time = io.receive_time()
		#info(str(time))
		errorcount = 0
	except (KeyboardInterrupt, ReloadException):
		raise
	except Exception as error_message:
		error(str(error_message))
		warning("couldn't get time from server")
	try:
		import pcf8523_adafruit # to set the RTC
		pcf8523_adafruit.set_from_timestruct(time)
	except (KeyboardInterrupt, ReloadException):
		raise
	except Exception as error_message:
		try:
			import ds3231_adafruit # to set the RTC
			ds3231_adafruit.set_from_timestruct(time)
		except (KeyboardInterrupt, ReloadException):
			raise
		except Exception as error_message:
			error(str(error_message))
			warning("couldn't set RTC")
			errorcount += 1
	check_error_count_and_reboot_if_too_high()
	return time

def show_signal_strength():
	rssi = get_values()[0]
	try:
		info("RSSI: " + str(rssi) + " dB") # receiving signal strength indicator
	except (KeyboardInterrupt, ReloadException):
		raise
	except Exception as error_message:
		error(str(error_message))
		warning("can't get signal strength")

def get_values():
	try:
		values = [ get_rssi() ]
	except (KeyboardInterrupt, ReloadException):
		raise
	except Exception as error_message:
		error(str(error_message))
		values = [ 0. ]
	myboxcar.accumulate(values)
	return values

def measure_string():
	values = get_values()
	return ", " + str(values[0])

def show_average_values():
	myboxcar.show_average_values()

def get_average_values():
	return myboxcar.get_average_values()

