#!/bin/bash -e

cd
mkdir -p build
cd ${HOME}/build

sudo apt install -y python3-dev python3-rpi.gpio python3-spidev python3-w1thermsensor i2c-tools

if [ ! -e "RPi-Hat-Thermocouple" ]; then
	#git clone git@github.com:mikelawrence/RPi-Hat-Thermocouple.git
	git clone https://github.com/mikelawrence/RPi-Hat-Thermocouple.git
else
	cd "RPi-Hat-Thermocouple" 
	git pull
fi

sudo apt install -y python3-picamera python-picamera
#sudo apt install -y python-pip exuberant-ctags
#cd ${HOME}/build
#git clone https://github.com/waveform80/picamera.git
#cd picamera
#make develop || /bin/true
#sudo make develop

sudo apt install -y python-opencv python-numpy python3-numpy

cd ${HOME}/build
if [ ! -e "pylepton" ]; then
	#git clone git@github.com:groupgets/pylepton.git
	git clone https://github.com/groupgets/pylepton.git
else
	cd "pylepton"
	git pull
fi

sudo apt install -y ffmpeg gnuplot

#GetThermal (for usb connected flir camera only):
# https://github.com/groupgets/GetThermal/wiki/Building-for-Raspberry-Pi
#sudo apt install -y qt5-default qtmultimedia5-dev qtdeclarative5-dev qml-module-qtquick-controls2 qml-module-qtmultimedia qml-module-qtquick-layouts qml-module-qtquick-window2 qml-module-qtquick-templates2 qml-module-qtgraphicaleffects libusb-1.0-0-dev git cmake libusb-1.0-0-dev
#sudo raspi-config
#    Select "Advanced Options"
#    Select "GL Driver"
#    Select "GL (Full KMS) OpenGL desktop driver with full KMS"
#    Select "ok"
#    Select "Finish"
#sudo reboot
#git clone https://github.com/groupgets/GetThermal.git
#cd GetThermal
#git submodule update --init
#cd libuvc
#mkdir build
#cd build
#cmake ..
#make
#cd ../..
#mkdir build
#cd build
#qmake ..
#make

# usb video class (uvc) cameras:
sudo apt install -y luvcview

# circuitpython:
cd ${HOME}/build
sudo apt install -y python-serial python3-serial
if [ ! -e circuitpython ]; then
	git clone https://github.com/adafruit/circuitpython.git
else
	cd circuitpython
	git pull
fi
cd ${HOME}/build
dir="v3.6.0"
filename="update-bootloader-circuitplay_m0-v3.6.0.uf2"
if [ ! -e $filename ]; then
	wget -q https://github.com/adafruit/uf2-samdx1/releases/download/$dir/$filename
fi
sudo mount /dev/sda /media && sudo cp $filename /media/ && sudo umount /media
#to unbrick:
#while /bin/true; do sudo mount /dev/sda /media && sudo cp update-bootloader-circuitplay_m0-v3.6.0.uf2 /media/ && sudo umount /media && break; done
dir="4.0.1"
filename="adafruit-circuitpython-circuitplayground_express-en_US-4.0.1.uf2"
if [ ! -e $filename ]; then
	wget -q https://github.com/adafruit/circuitpython/releases/download/$dir/$filename
fi
sudo mount /dev/sda /media && sudo cp $filename /media/ && sudo umount /media

# adafruit max31856 thermocouple board:
sudo apt install -y build-essential python-dev python-smbus python3-venv python3-pip
cd ${HOME}/build
if [ ! -e Adafruit_Python_MAX31856 ]; then
	git clone https://github.com/johnrbnsn/Adafruit_Python_MAX31856
	cd Adafruit_Python_MAX31856
else
	cd Adafruit_Python_MAX31856
	git pull
fi
#python3 -m venv env_py3
#source env_py3/bin/activate
#pip install -r requirements.txt
#pip install ./.
#sudo pip3 install rpi.gpio
sudo pip3 install Adafruit_GPIO

# for plotting temperatures:
sudo apt install -y eog imagemagick

# recommended for high radiation environments:
sudo apt install -y watchdog
sudo systemctl enable watchdog
sudo systemctl start watchdog

cat <<here

# change the following in system.conf:

CrashReboot=yes
RuntimeWatchdogSec=15
ShutdownWatchdogSec=15

here
sleep 3
sudo vim /etc/systemd/system.conf
echo "now reboot for the systemd configuration to take effect"

#echo "raspistill -rot 180 --nopreview -o pic.jpg"

