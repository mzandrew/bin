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

declare PREFIX="/usr"

cd ~/build/openocd
nice ./configure --prefix=$PREFIX --enable-ftdi --enable-buspirate --enable-ft232r --enable-armjtagew --enable-bcm2835gpio --disable-stlink --disable-ti-icdi --disable-ulink --disable-usb-blaster-2 --disable-vsllink --disable-xds110 --disable-osbdm --disable-opendous --disable-aice --disable-usbprog --disable-rlink --disable-cmsis-dap --disable-kitprog --disable-usb-blaster --disable-presto --disable-openjtag --disable-jlink --disable-parport --disable-parport-giveio --disable-jtag_vpi --disable-amtjtagaccel --disable-zy1000-master --disable-zy1000 --disable-ioutil --disable-ep93xx --disable-at91rm9200 --disable-imx_gpio --disable-gw16012 --disable-oocd_trace --disable-sysfsgpio

nice make
sudo nice make install

declare file="644" dir="755"
sudo find $PREFIX/share/openocd -type f -exec chmod --changes $file {} + -o -type d -exec chmod --changes $dir {} +
sudo cp -a $PREFIX/share/openocd/contrib/60-openocd.rules /etc/udev/rules.d/

ls -lart $PREFIX/bin/openocd $PREFIX/share/openocd /etc/udev/rules.d/60-openocd.rules

