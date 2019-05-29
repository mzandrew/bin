#!/bin/bash -e

declare -i MiB=1024

function add_swap_if_necessary {
	if [ ! -e /swap ]; then
		echo "generating $MiB MiB /swap file..."
		sudo dd if=/dev/zero of=/swap bs=$((1024*1024)) count=$MiB
		sudo chmod 600 /swap
		sudo mkswap /swap
		sudo swapon /swap
		sudo sed -ie '/swapon/{h;s/.*/swapon \/swap/};${x;/^$/{s/.*/swapon \/swap/;H};x}' /etc/rc.local
	fi
}

function install_packages_0 {
	sudo apt -y install vim
	#sudo sed -i "s/gb/us/" /etc/default/keyboard
	sudo raspi-config # enable sshd; change video memory to 16MB; change hostname; enable spi+i2c+1wire
}

function install_packages_1 {
	sudo apt-get clean
	sudo apt -y install mlocate git subversion rsync lm-sensors
	sudo apt -y update
	sudo apt -y upgrade
	sudo apt -y install vpnc firefox-esr nfs-common
	sudo apt-get -y autoremove
	sudo apt-get clean
}

#sudo useradd mza
#sudo usermod mza -a -G sudo

install_packages_0
# reboot, and continue:
install_packages_1
add_swap_if_necessary

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
#ln -s ../build/bin/rpi

cat >> ~/.bashrc <<HERE

if [ -e $HOME/build/bin/nofizbin/bashrc ]; then
	. $HOME/build/bin/nofizbin/bashrc
fi

HERE

