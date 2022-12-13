# written 2022-12-07 by mza
# based on lora.py and lora_transceiver_basic_test.py
# last updated 2022-12-13 by mza

import time
import board
import busio
import digitalio
import adafruit_rfm9x
import gc

PREFIX = "SCOOPY"
SUFFIX = "BOOPS"
node_type = "gathering"
BAUD_RATE = 4*57600
RADIO_FREQ_MHZ = 905.0 # (902-928 MHz in US/MEX/CAN)
TX_POWER_DBM = 5 # [5, 23]
N = 6
ina260_N = 6
delay = 10
ina260_bins = 2
ina260_address = 0x40
should_use_ina260 = True

def ina260_adafruit_get_values(bin=0):
	values = [ ina260.current, ina260.voltage, ina260.power ]
	#myboxcar.accumulate(values, bin)
	return values

def ina260_adafruit_show_average_values(bin=0):
	#myboxcar.show_average_values(bin)
	print("0, 0, 0")

def ina260_adafruit_get_average_values(bin=0):
	#return myboxcar.get_average_values(bin)
	return [ 0, 0, 0 ]

message_id = 1
def send_a_message(message):
	global message_id
	message_id += 1
	message_id_string = "[" + str(message_id) + "] "
	message_with_prefix_and_suffix = PREFIX + message_id_string + message + SUFFIX
	print("sending: " + message_id_string + message)
	rfm9x.send(bytes(message_with_prefix_and_suffix, "utf-8"))

def setup(spi, cs, reset, frequency, baudrate, tx_power_dbm):
	gc.collect()
	print("mem free setup(): " + str(gc.mem_free()))
	global rfm9x
	rfm9x = adafruit_rfm9x.RFM9x(spi=spi, cs=cs, reset=reset, frequency=frequency, baudrate=baudrate)
	rfm9x.tx_power = tx_power_dbm

def loop():
	gc.collect()
	print("mem free loop(): " + str(gc.mem_free()))
	i = 0
	while True:
		if ina260_is_available:
			ina260_adafruit_get_values(0)
		if 0==i%N:
			print("doing something")
			if ina260_is_available:
				ina260_adafruit_show_average_values(0)
				values = ina260_adafruit_get_average_values(0)
				string = str(values)
				#send_a_message("ina260bin0 " + string)
				ina260_adafruit_get_values(1)
#				ina260_adafruit_show_average_values(1)
#				values = ina260_adafruit_get_average_values(1)
#				string = str(values)
#				send_a_message("ina260bin1 " + string)
		else:
			print("did nothing")
		i += 1
		time.sleep(delay)

if __name__ == "__main__":
	spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
	CS = digitalio.DigitalInOut(board.RFM9X_CS)
	RESET = digitalio.DigitalInOut(board.RFM9X_RST)
	gc.collect()
	setup(spi, CS, RESET, RADIO_FREQ_MHZ, BAUD_RATE, TX_POWER_DBM)
	i2c = busio.I2C(board.SCL, board.SDA)
	global ina260_is_available
	ina260_is_available = False
	gc.collect()
	print("mem free ina260: " + str(gc.mem_free()))
	if should_use_ina260:
		try:
			import adafruit_ina260
			global ina260
			ina260 = adafruit_ina260.INA260(i2c_bus=i2c, address=ina260_address)
			adafruit_ina260.INA260.mode = adafruit_ina260.Mode.TRIGGERED
			adafruit_ina260.INA260.current_conversion_time = adafruit_ina260.ConversionTime.TIME_8_244_ms
			adafruit_ina260.INA260.voltage_conversion_time = adafruit_ina260.ConversionTime.TIME_8_244_ms
			adafruit_ina260.INA260.averaging_count = adafruit_ina260.AveragingCount.COUNT_1024
		except:
			print("warning: can't talk to ina260 at address " + str(ina260_address))
		try:
			global myboxcar
			gc.collect()
			print("mem free boxcar: " + str(gc.mem_free()))
			import boxcar
			gc.collect()
			print("mem free boxcar: " + str(gc.mem_free()))
			gc.collect()
			print("mem free boxcar: " + str(gc.mem_free()))
			myboxcar = boxcar.boxcar(3, ina260_N, "ina260", ina260_bins)
			gc.collect()
			print("mem free boxcar: " + str(gc.mem_free()))
			ina260_is_available = True
		except MemoryError as error_message:
			print("MemoryError: " + str(error_message))
		except:
			print("warning: can't setup boxcars")
#	if ina260_is_available:
#		ina260_adafruit.get_values(1)
	loop()

