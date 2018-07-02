#!/bin/bash -e

#sudo useradd mza
#sudo usermod mza -a -G sudo

sudo apt -y install vim
#sudo sed -i "s/gb/us/" /etc/default/keyboard
sudo raspi-config # enable sshd; change video memory to 16MB; change hostname; enable spi+i2c+1wire

# reboot, and continue:

sudo apt -y install mlocate git subversion rsync lm-sensors
sudo apt -y update
sudo apt -y upgrade
sudo apt -y install vpnc firefox-esr
sudo apt -y install nfs-common

cd
mkdir -p build
cd build
if [ ! -e bin ]; then
	git clone https://github.com/mzandrew/bin.git
fi
cd
mkdir -p bin
cd bin
ln -s ../build/bin/generic
#ln -s ../build/bin/rpi

cat >> ~/.bashrc <<HERE
if [ -e $HOME/build/bin/nofizbin/bashrc ]; then
	. $HOME/build/bin/nofizbin/bashrc
fi
HERE

