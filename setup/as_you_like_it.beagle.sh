#!/bin/bash -e

if [ ! -e /swap ]; then
	sudo dd if=/dev/zero of=/swap bs=$((1024*1024)) count=1024
	sudo mkswap /swap
	sudo swapon /swap
	sudo sed -ie '/swapon/{h;s/.*/swapon \/swap/};${x;/^$/{s/.*/swapon \/swap/;H};x}' /etc/rc.local
fi

#sudo useradd mza
#sudo usermod mza -a -G sudo

sudo apt-get -y install vim
sudo apt-get -y install mlocate git subversion rsync lm-sensors
sudo apt-get -y update
sudo apt-get -y upgrade
sudo apt-get -y install vpnc firefox-esr nfs-common
sudo apt-get autoremove
sudo apt-get clean

cd
mkdir -p build
cd build
if [ ! -e bin ]; then
	git clone https://github.com/mzandrew/bin.git
fi
cd
mkdir -p bin
cd bin
if [ ! -e generic ]; then
	ln -s ../build/bin/generic
fi

cat >> ~/.bashrc <<HERE
if [ -e $HOME/build/bin/nofizbin/bashrc ]; then
	. $HOME/build/bin/nofizbin/bashrc
fi
HERE

