# 2022-12-07to2023-01-07bymza
import time,board,busio,digitalio,adafruit_rfm9x,gc
import adafruit_ina260

PRE="SCOOPY"
SUF="BOOPS"
B=4*57600
RF=905.0
T=5 #[5,20]
N=51
d=10
n=3

def r(N):
	return range(N)

def bc_setup(numitems):
	global items
	items=numitems
	global av
	av=[[0. for a in r(items)] for b in r(N)]
	global sums
	sums=[0. for a in r(items)]
	global Nacc
	Nacc=0
	gc.collect()

def bc_acc(vals):
	global Nacc
	Nacc+=1
	global av
	av.append(vals[:])
	for i in r(items):
		sums[i]=0.
		for j in range(1,len(av)):
			sums[i]+=av[j][i]
	av.pop(0)
	gc.collect()

def bc_get_avg_vals():
	if Nacc<N:
		n=Nacc
	else:
		n=N
	if 0==n:
		return
	avg_vals=[sums[i]/float(n) for i in r(items)]
	return avg_vals

def ina_get_vals():
	vals=[ina.current,ina.voltage,ina.power]
	bc_acc(vals)
	return vals

def ina_gav():
	return bc_get_avg_vals()

def ina_show_avg_vals():
	print(str(ina_gav()))

msgid=0
def send(msg):
	global msgid
	msgid+=1
	msgid_str="node"+str(n)+"["+str(msgid)+"] "
	print(msgid_str + msg)
	rfm9x.send(bytes(PRE+msgid_str+msg+SUF,"utf-8"))

rfm9x=adafruit_rfm9x.RFM9x(spi=busio.SPI(board.SCK,MOSI=board.MOSI,MISO=board.MISO),cs=digitalio.DigitalInOut(board.RFM9X_CS),reset=digitalio.DigitalInOut(board.RFM9X_RST),frequency=RF,baudrate=B)
rfm9x.tx_power=T
gc.collect()
i2c=busio.I2C(board.SCL,board.SDA)
gc.collect()
global ina
ina=adafruit_ina260.INA260(i2c_bus=i2c,address=0x40)
gc.collect()
bc_setup(3)
gc.collect()
i=1
while True:
	ina_get_vals()
	if 0==i%N:
		ina_show_avg_vals()
		send("ina260bin0 " + str(ina_gav()))
	i+=1
	time.sleep(d)

