#!/bin/bash -e

# last updated 2018-11-14 by mza

function install_prerequisites_apt {
	sudo nice apt -y install libtool autoconf automake libusb-1.0 libusb-dev libtcl8.5 tcl8.5 make gcc clang pkg-config texinfo libftdi1
}

function install_prerequisites_yum {
	sudo nice yum -y install libtool autoconf automake make gcc clang texinfo libusb tcl-devel tcl pkgconfig libftdi
	#sudo nice yum -y install openocd # version is Open On-Chip Debugger 0.5.0 (2011-12-19-21:28) in SL6.10
	#sudo nice yum -y install openocd # version is Open On-Chip Debugger 0.8.0 (2014-04-29-12:22) in SL7.3 and SL7.5
	# ~2018 git version needs automake>=1.14 and SL7.3 only has 1.13
	# libusb-devel
}

function install_prerequisites_pac {
	echo "archlinux version is not done yet"
	exit 1
}

declare -i redhat=0 SL6=0 SL7=0 deb=0
if [ -e /etc/redhat-release ]; then
	redhat=1
	set +e
	SL6=$(grep -c "Scientific Linux release 6" /etc/redhat-release)
	SL7=$(grep -c "Scientific Linux release 7" /etc/redhat-release)
	set -e
elif [ -e /etc/debian_version ]; then
	deb=1
elif [ -e /etc/arch-release ]; then
	arch=1
else
	echo "what kind of linux is this?"
	exit 1
fi
if [ $deb -gt 0 ]; then
	install_prerequisites_apt
elif [ $redhat -gt 0 ]; then
	install_prerequisites_yum
elif [ $arch -gt 0 ]; then
	install_prerequisites_pac
fi

declare build="${HOME}/build"
declare openocd="${HOME}/build/openocd"

mkdir -p $build

if [ -e $openocd ];then
	cd $openocd
	git pull
else
	cd $build
	git clone git://git.code.sf.net/p/openocd/code openocd
	git revert 5be455a710c57bbbbd49c2d671b42098db7be5dc
	#tar cf openocd.tar openocd
	cd $openocd
	nice ./bootstrap
fi

declare PREFIX="/usr"

cd $openocd
nice ./configure --prefix=$PREFIX --enable-ftdi --enable-buspirate --enable-ft232r --enable-armjtagew --enable-bcm2835gpio --disable-stlink --disable-ti-icdi --disable-ulink --disable-usb-blaster-2 --disable-vsllink --disable-xds110 --disable-osbdm --disable-opendous --disable-aice --disable-usbprog --disable-rlink --disable-cmsis-dap --disable-kitprog --disable-usb-blaster --disable-presto --disable-openjtag --disable-jlink --disable-parport --disable-parport-giveio --disable-jtag_vpi --disable-amtjtagaccel --disable-zy1000-master --disable-zy1000 --disable-ioutil --disable-ep93xx --disable-at91rm9200 --disable-imx_gpio --disable-gw16012 --disable-oocd_trace --disable-sysfsgpio

nice make
sudo nice make install

declare file="644" dir="755"
sudo find $PREFIX/share/openocd -type f -exec chmod --changes $file {} + -o -type d -exec chmod --changes $dir {} +
sudo cp -a $PREFIX/share/openocd/contrib/60-openocd.rules /etc/udev/rules.d/

ls -lart $PREFIX/bin/openocd $PREFIX/share/openocd /etc/udev/rules.d/60-openocd.rules

