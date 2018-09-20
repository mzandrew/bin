#!/bin/bash -e

function install_packages {
	sudo nice apt -y install libtool autoconf automake libusb-1.0 libtcl8.5 tcl8.5 make gcc clang pkg-config texinfo
}

install_packages

cd
mkdir -p build

if [ ! -e ~/build/openocd ];then
	cd ~/build
	git clone git://git.code.sf.net/p/openocd/code openocd
	cd openocd
	nice ./bootstrap
fi

cd ~/build/openocd
nice ./configure --enable-ftdi --enable-buspirate
nice make
sudo nice make install

declare file="644" dir="755"
sudo find /usr/local/share/openocd -type f -exec chmod --changes $file {} + -o -type d -exec chmod --changes $dir {} +

ls -lart /usr/local/bin/openocd /usr/local/share/openocd 

