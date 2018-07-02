#!/bin/bash -e

#sudo useradd mza
#sudo usermod mza -a -G sudo

sudo apt-get -y install vim
sudo apt-get -y install mlocate git subversion rsync lm-sensors
sudo apt-get -y update
sudo apt-get -y upgrade
sudo apt-get -y install vpnc firefox-esr

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

cat >> ~/.bashrc <<HERE
if [ -e $HOME/build/bin/nofizbin/bashrc ]; then
	. $HOME/build/bin/nofizbin/bashrc
fi
HERE

