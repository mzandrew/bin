# written 2022-07 by mza
# basic bits taken from adafruit's rfm9x_simpletest.py by Tony DiCola and rfm9x_node1_ack.py by Jerry Needell
# more help from https://learn.adafruit.com/multi-device-lora-temperature-network/using-with-adafruitio
# last updated 2022-12-21 by mza

import time
import board
import busio
import adafruit_rfm9x
import re
import generic
from DebugInfoWarningError24 import debug, info, warning, error, debug2, debug3, set_verbosity, create_new_logfile_with_string

PREFIX = "SCOOPY"
SUFFIX = "BOOPS"
USE_ACKNOWLEDGE = False

def setup(spi, cs, reset, frequency, baudrate, tx_power_dbm, airlift_available, RTC_available, type_of_node, adafruit_io_prefix, mynodeid):
	global rfm9x
	rfm9x = adafruit_rfm9x.RFM9x(spi=spi, cs=cs, reset=reset, frequency=frequency, baudrate=baudrate)
	rfm9x.tx_power = tx_power_dbm
	#rfm9x.signal_bandwidth = 62500
	#rfm9x.coding_rate = 6
	#rfm9x.spreading_factor = 8
	#rfm9x.enable_crc = True
	if USE_ACKNOWLEDGE:
		rfm9x.ack_delay = 0.1
		if "LORASEND"==label:
			rfm9x.node = 2
			rfm9x.destination = 1
		else:
			time.sleep(2)
			rfm9x.node = 1
			rfm9x.destination = 2
		info("we are node " + str(rfm9x.node))
	global airlift_is_available
	airlift_is_available = airlift_available
	if airlift_is_available:
		global airlift
		import airlift
	global RTC_is_available
	RTC_is_available = RTC_available
	if RTC_is_available:
		global pcf8523_adafruit
		import pcf8523_adafruit
	global node_type
	node_type = type_of_node
	global my_adafruit_io_prefix
	my_adafruit_io_prefix = adafruit_io_prefix
	global nodeid
	nodeid = mynodeid

def idle():
	rfm9x.idle()

def sleep():
	rfm9x.sleep()

def receive(timeout):
	if USE_ACKNOWLEDGE:
		packet = rfm9x.receive(with_ack=True, timeout=timeout)
	else:
		packet = rfm9x.receive(timeout=timeout)
	return packet

def send_a_message(message):
	global message_id
	try:
		message_id += 1
	except (KeyboardInterrupt, ReloadException):
		raise
	except Exception as error_message:
		message_id = 1
	message_id_string = "node" + str(nodeid) + "[" + str(message_id) + "] "
	message_with_prefix_and_suffix = PREFIX + message_id_string + message + SUFFIX
	if 252<len(message_with_prefix_and_suffix):
		warning("should truncate or parcel message because it is too long")
	info("sending: " + message_id_string + message)
	if USE_ACKNOWLEDGE:
		if rfm9x.send_with_ack(bytes(message_with_prefix_and_suffix, "utf-8")):
			info("ack received")
		else:
			info("no ack received")
	else:
		rfm9x.send(bytes(message_with_prefix_and_suffix, "utf-8"))

def send_a_message_with_timestamp(message):
	if RTC_is_available:
		timestring = pcf8523_adafruit.get_timestring3()
		message = timestring + " " + message
	send_a_message(message)

previously_received_message_id = {}
total_skipped_messages = {}
skipped_messages = {}
def decode_a_message(packet):
	global previously_received_message_id
	global total_skipped_messages
	global skipped_messages
	current_message_id = 0
	try:
		rssi = rfm9x.last_rssi
	except (KeyboardInterrupt, ReloadException):
		raise
	except Exception as error_message:
		rssi = 0
	try:
		packet_text = str(packet, "ascii")
		match = re.search("^" + PREFIX + "node([0-9]+)\[([0-9]+)\](.*)" + SUFFIX + "$", packet_text)
		if match:
			mynodeid = match.group(1)
			try:
				previously_received_message_id[mynodeid]
			except (KeyboardInterrupt, ReloadException):
				raise
			except Exception as error_message:
				previously_received_message_id[mynodeid] = 0
			try:
				total_skipped_messages[mynodeid]
			except (KeyboardInterrupt, ReloadException):
				raise
			except Exception as error_message:
				total_skipped_messages[mynodeid] = 0
			try:
				skipped_messages[mynodeid]
			except (KeyboardInterrupt, ReloadException):
				raise
			except Exception as error_message:
				skipped_messages[mynodeid] = 0
			current_message_id = int(match.group(2))
			message = match.group(3)
			skipped_messages[mynodeid] = current_message_id - previously_received_message_id[mynodeid] - 1
			#debug("previously_received_message_id[" + str(mynodeid) + "]: " + str(previously_received_message_id[mynodeid]))
			#debug("current_message_id: " + str(current_message_id))
			if 0<skipped_messages[mynodeid]:
				total_skipped_messages[mynodeid] += skipped_messages[mynodeid]
				#warning("skipped[" + str(mynodeid) + "] " + str(skipped_messages[mynodeid]) + " message(s)")
				if current_message_id:
					percentage = int(1000.0 * total_skipped_messages[mynodeid] / current_message_id)/10.0
				else:
					percentage = "?"
				warning("for node" + str(mynodeid) + ": skipped " + str(skipped_messages[mynodeid]) + " message(s); total skipped: " + str(total_skipped_messages[mynodeid]) + "/" + str(current_message_id) + " = " + str(percentage) + "%")
				if airlift_is_available:
					try:
						airlift.post_data(my_adafruit_io_prefix + "-" + str(mynodeid) + "skipped", skipped_messages[mynodeid])
					except (KeyboardInterrupt, ReloadException):
						raise
					except Exception as error_message:
						warning("unable to post skipped data")
						airlift.show_network_status()
						error(str(error_message))
			info("received: node" + str(mynodeid) + "[" + str(current_message_id) + "]" + message + " RSSI=" + str(rssi) + "dBm")
			previously_received_message_id[mynodeid] = current_message_id
			if "uplink"==node_type:
				parse(mynodeid, message, rssi)
		else:
			debug("received: " + packet_text + " RSSI=" + str(rssi) + "dBm")
	except (KeyboardInterrupt, ReloadException):
		raise
	except Exception as error_message:
		warning("message garbled RSSI=" + str(rssi) + "dBm")
		error(str(error_message))
		if airlift_is_available:
			try:
				airlift.post_data(my_adafruit_io_prefix + "-garb-rssi", rssi)
			except (KeyboardInterrupt, ReloadException):
				raise
			except Exception as error_message:
				warning("unable to post garb_rssi data")
				airlift.show_network_status()
				error(str(error_message))
		#info("total skipped messages: " + str(total_skipped_messages[mynodeid]))
	return current_message_id

def post_rssi(mynodeid, rssi):
	try:
		airlift.post_data(my_adafruit_io_prefix + "-" + str(mynodeid) + "rssi", rssi)
	except (KeyboardInterrupt, ReloadException):
		raise
	except Exception as error_message:
		warning("couldn't post data for lora rssi")
		airlift.show_network_status()
		error(str(error_message))

def parse_bme680(mynodeid, message, rssi):
	match = re.search("bme680 \[([0-9.]+), ([0-9.]+), ([0-9.]+),", message)
	if match:
		temp = float(match.group(1))
		hum = float(match.group(2))
		pres = float(match.group(3))
		info("temperature: " + str(temp) + " C")
		info("humidity: " + str(hum) + " %RH")
		info("presure: " + str(pres) + " ATM")
		if airlift_is_available:
			try:
				airlift.post_data(my_adafruit_io_prefix + "-" + str(mynodeid) + "temp", temp)
				airlift.post_data(my_adafruit_io_prefix + "-" + str(mynodeid) + "hum", hum)
				airlift.post_data(my_adafruit_io_prefix + "-" + str(mynodeid) + "pres", pres)
			except (KeyboardInterrupt, ReloadException):
				raise
			except Exception as error_message:
				warning("couldn't post data for remote bme680")
				airlift.show_network_status()
				error(str(error_message))
			#post_rssi(mynodeid, rssi)
		return True
	else:
		return False

def parse_as7341(mynodeid, message, rssi):
	match = re.search("as7341 \[([0-9.]+), ([0-9.]+), ([0-9.]+), ([0-9.]+), ([0-9.]+), ([0-9.]+), ([0-9.]+), ([0-9.]+), ([0-9.]+), ([0-9.]+)\]", message)
	if match:
		nm415 = float(match.group(1))
		nm445 = float(match.group(2))
		nm480 = float(match.group(3))
		nm515 = float(match.group(4))
		nm555 = float(match.group(5))
		nm590 = float(match.group(6))
		nm630 = float(match.group(7))
		nm680 = float(match.group(8))
		clear = float(match.group(9))
		nir   = float(match.group(10))
		info("nm415: " + str(nm415))
		info("nm445: " + str(nm445))
		info("nm480: " + str(nm480))
		info("nm515: " + str(nm515))
		info("nm555: " + str(nm555))
		info("nm590: " + str(nm590))
		info("nm630: " + str(nm630))
		info("nm680: " + str(nm680))
		info("clear: " + str(clear))
		info("nir: " + str(nir))
		if airlift_is_available:
			try:
				pass
				airlift.post_data(my_adafruit_io_prefix + "-" + str(mynodeid) + "clear", clear)
			except (KeyboardInterrupt, ReloadException):
				raise
			except Exception as error_message:
				warning("couldn't post data for remote as7341")
				airlift.show_network_status()
				error(str(error_message))
			#post_rssi(mynodeid, rssi)
		return True
	else:
		return False

def parse_ina260(mynodeid, message, rssi):
	match = re.search("ina260bin([0-9]+) \[([-0-9.]+), ([-0-9.]+),", message)
	if match:
		mybin = int(match.group(1))
		current = float(match.group(2))
		voltage = float(match.group(3))
		#info("bin: " + str(mybin))
		info("current: " + str(current) + " mA")
		info("voltage: " + str(voltage) + " V")
		if airlift_is_available:
			try:
				pass
				airlift.post_data(my_adafruit_io_prefix + "-" + str(mynodeid) + "current" + str(mybin), current)
				voltage = generic.fround(voltage, 0.001)
				if 0==mybin:
					airlift.post_data(my_adafruit_io_prefix + "-" + str(mynodeid) + "batt", voltage)
			except (KeyboardInterrupt, ReloadException):
				raise
			except Exception as error_message:
				warning("couldn't post data for remote ina260")
				airlift.show_network_status()
				error(str(error_message))
			if 0==mybin:
				post_rssi(mynodeid, rssi)
		return True
	else:
		return False

def parse_ping_and_respond(mynodeid, message, rssi):
	match = re.search(" ping", message)
	if match:
		send_a_message_with_timestamp("pong rssi=" + str(rssi))
		if airlift_is_available:
			try:
				pass
				#airlift.post_data(my_adafruit_io_prefix + "-" + str(mynodeid) + "ping", rssi)
				#post_rssi(mynodeid, rssi)
			except (KeyboardInterrupt, ReloadException):
				raise
			except Exception as error_message:
				warning("couldn't post data for received ping")
				airlift.show_network_status()
				error(str(error_message))
		return True
	else:
		return False

def parse_lora_rssi_pingpong(mynodeid, message, rssi):
	#info(message)
	match = re.search(" lora-rssi-(ping|pong) \[([-0-9.]+)\]", message)
	if match:
		pingpong = match.group(1)
		lora_pingpong_rssi = match.group(2)
		lora_pingpong_rssi = int(lora_pingpong_rssi)
		#info(str(lora_pingpong_rssi))
		if "pong"==pingpong:
			return True
		if airlift_is_available:
			try:
				pass
				#airlift.post_data(my_adafruit_io_prefix + "-" + str(mynodeid) + pingpong + "-rssi", lora_pingpong_rssi)
				#post_rssi(mynodeid, rssi)
			except (KeyboardInterrupt, ReloadException):
				raise
			except Exception as error_message:
				warning("couldn't post data for received " + pingpong + " rssi")
				airlift.show_network_status()
				error(str(error_message))
		return True
	else:
		return False

def parse_geotagged_lora_rssi_pingpong(mynodeid, message, rssi):
	#info(message)
	match = re.search(" lora-rssi-(ping|pong) \[([-0-9.]+),([-0-9.]+),([-0-9.]+),([-0-9.]+)\]", message)
	if match:
		pingpong = match.group(1)
		lora_pingpong_rssi = match.group(2)
		lora_pingpong_rssi = int(lora_pingpong_rssi)
		lat = float(match.group(3))
		lon = float(match.group(4))
		ele = float(match.group(5))
		location = [ lat, lon, ele ]
		#info(str(lora_pingpong_rssi))
		if "pong"==pingpong:
			return True
		if airlift_is_available:
			try:
				airlift.post_geolocated_data(my_adafruit_io_prefix + "-" + str(mynodeid) + pingpong + "-rssi", location, lora_pingpong_rssi)
				#post_rssi(mynodeid, rssi)
			except (KeyboardInterrupt, ReloadException):
				raise
			except Exception as error_message:
				warning("couldn't post data for received " + pingpong + " rssi")
				airlift.show_network_status()
				error(str(error_message))
		return True
	else:
		return False

def parse(mynodeid, message, rssi):
	info(message)
	if parse_bme680(mynodeid, message, rssi):
		return True
	if parse_as7341(mynodeid, message, rssi):
		return True
	if parse_ina260(mynodeid, message, rssi):
		return True
	if parse_ping_and_respond(mynodeid, message, rssi):
		return True
	if parse_lora_rssi_pingpong(mynodeid, message, rssi):
		return True
	if parse_geotagged_lora_rssi_pingpong(mynodeid, message, rssi):
		return True
	return False

