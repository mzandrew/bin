# written 2022-12-07 to 2022-12-13 by mza
import time, board, busio, digitalio, adafruit_rfm9x, gc

PREFIX = "SCOOPY"
SUFFIX = "BOOPS"
BAUD = 4*57600
RF = 905.0 # [902,928]
TXDBM = 5 # [5, 23]
N = 6
ina_N = 4
delay = 10
ina_bins = 2
nodeid = 3

def bc_setup(numitems, numbins=1):
	global items
	items = numitems
	global bins
	bins = numbins
	global acc_vals
	acc_vals = [ [ [ 0. for a in range(items) ] for b in range(N) ] for c in range(bins) ]
	global sums
	sums = [ [ 0. for a in range(items) ] for b in range(bins) ]
	global Nacc
	Nacc = [ 0 for a in range(bins) ]
	gc.collect()

def bc_acc(vals, mybin=0):
	global Nacc
	Nacc[mybin] += 1
	global acc_vals
	acc_vals[mybin].append(vals[:])
	for i in range(items):
		sums[mybin][i] = 0.
		for j in range(1, len(acc_vals[mybin])):
			sums[mybin][i] += acc_vals[mybin][j][i]
	acc_vals[mybin].pop(0)
	gc.collect()

def bc_get_avg_vals(mybin=0):
	if Nacc[mybin]<N:
		n = Nacc[mybin]
	else:
		n = N
	if 0==n:
		return
	avg_vals = [ sums[mybin][i]/float(n) for i in range(items) ]
	return avg_vals

def ina_get_vals(mybin=0):
	vals = [ ina.current, ina.voltage, ina.power ]
	bc_acc(vals, mybin)
	return vals

def ina_get_avg_vals(mybin=0):
	return bc_get_avg_vals(mybin)

def ina_show_avg_vals(mybin=0):
	print(str(ina_get_avg_vals(mybin)))

msgid = 0
def send(msg):
	global msgid
	msgid += 1
	msgid_str = "node" + str(nodeid) + "[" + str(msgid) + "] "
	print(msgid_str + msg)
	rfm9x.send(bytes(PREFIX + msgid_str + msg + SUFFIX, "utf-8"))

def loop():
	i = 0
	while True:
		if ina_exists:
			ina_get_vals(0)
		if 0==i%N:
			print("yup")
			if ina_exists:
				ina_show_avg_vals(0)
				send("ina260bin0 " + str(ina_get_avg_vals(0)))
				time.sleep(2)
				ina_get_vals(1)
				ina_show_avg_vals(1)
				send("ina260bin1 " + str(ina_get_avg_vals(1)))
				ina_get_vals(1)
		else:
			print("nope")
		i += 1
		time.sleep(delay)

if __name__ == "__main__":
	rfm9x = adafruit_rfm9x.RFM9x(spi=busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO), cs=digitalio.DigitalInOut(board.RFM9X_CS), reset=digitalio.DigitalInOut(board.RFM9X_RST), frequency=RF, baudrate=BAUD)
	rfm9x.tx_power = TXDBM
	gc.collect()
	i2c = busio.I2C(board.SCL, board.SDA)
	ina_exists = False
	try:
		import adafruit_ina260
		gc.collect()
		global ina
		ina = adafruit_ina260.INA260(i2c_bus=i2c, address=0x40)
		gc.collect()
		ina_exists = True
	except:
		print("can't setup ina260")
		raise
	try:
		gc.collect()
		bc_setup(3, ina_bins)
		gc.collect()
	except:
		print("can't setup boxcar")
		raise
	if ina_exists:
		ina_get_vals(1)
	loop()

