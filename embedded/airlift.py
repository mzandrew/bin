#!/usr/bin/env python3

# written 2021-05-01 by mza
# last updated 2021-05-01 by mza

from adafruit_esp32spi import adafruit_esp32spi
from adafruit_esp32spi import adafruit_esp32spi_wifimanager
import adafruit_requests as requests
import adafruit_esp32spi.adafruit_esp32spi_socket as socket
#import rtc

def setup_airlift():
	global wifi
	global secrets
	if not should_use_airlift:
		return False
	# from https://github.com/ladyada/Adafruit_CircuitPython_ESP32SPI/blob/master/examples/esp32spi_localtime.py
	# and https://learn.adafruit.com/adafruit-airlift-featherwing-esp32-wifi-co-processor-featherwing?view=all
	try:
		from secrets import secrets
	except ImportError:
		print("WiFi secrets are kept in secrets.py, please add them there!")
		return False
	try:
		esp32_cs = digitalio.DigitalInOut(board.D13)
		esp32_ready = digitalio.DigitalInOut(board.D11)
		esp32_reset = digitalio.DigitalInOut(board.D12)
		spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
		esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)
		#if esp.status == adafruit_esp32spi.WL_IDLE_STATUS:
			#print("ESP32 found and in idle mode")
			#print("Firmware vers.", esp.firmware_version)
			#print("MAC addr:", [hex(i) for i in esp.MAC_address])
		#for ap in esp.scan_networks():
		#	print("\t%s\t\tRSSI: %d" % (str(ap['ssid'], 'utf-8'), ap['rssi']))
		print("Connecting to " + secrets["ssid"] + " ...")
		while not esp.is_connected:
			try:
				esp.connect_AP(secrets["ssid"], secrets["password"])
				#print(".", end = "")
				#time.sleep(2)
			except RuntimeError as e:
				print("could not connect to AP, retrying: ", e)
				continue
		#print("Connected to", str(esp.ssid, 'utf-8'), "\tRSSI:", esp.rssi)
		print("My IP address is", esp.pretty_ip(esp.ip_address))
		#print("IP lookup adafruit.com: %s" % esp.pretty_ip(esp.get_host_by_name("adafruit.com")))
		#print("Ping google.com: %d ms" % esp.ping("google.com"))
		#requests.set_socket(socket, esp)
		#TEXT_URL = "http://wifitest.adafruit.com/testwifi/index.html"
		#print("Fetching text from", TEXT_URL)
		#r = requests.get(TEXT_URL)
		#print("-" * 40)
		#print(r.text)
		#print("-" * 40)
		#r.close()
		import adafruit_rgbled
		from adafruit_esp32spi import PWMOut
		RED_LED = PWMOut.PWMOut(esp, 26)
		GREEN_LED = PWMOut.PWMOut(esp, 25)
		BLUE_LED = PWMOut.PWMOut(esp, 27)
		status_light = adafruit_rgbled.RGBLED(RED_LED, BLUE_LED, GREEN_LED)
		wifi = adafruit_esp32spi_wifimanager.ESPSPI_WiFiManager(esp, secrets, status_light)
		#DATA_SOURCE = "https://www.google.com/index.html"
		#try:
		#	response = wifi.get(DATA_SOURCE)
		#except:
		#	wifi.reset()
	except:
		return False
	return True

def post_data(data):
	if not airlift_is_available:
		return
	try:
		#feed = "heater"
		feed = "test"
		payload = {"value": data}
		url = "https://io.adafruit.com/api/v2/" + secrets["aio_username"] + "/feeds/" + feed + "/data"
		response = wifi.post(url, json=payload, headers={"X-AIO-KEY": secrets["aio_key"]})
		#print(response.json())
		response.close()
	except:
		error("couldn't perform POST operation")

