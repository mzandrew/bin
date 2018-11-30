#!/bin/bash -e

# last updated 2018-11-29 by mza

function install_prerequisites_apt {
	sudo nice apt -y install libtool autoconf automake libusb-1.0 libusb-dev libtcl8.5 tcl8.5 make gcc clang pkg-config texinfo libftdi1
}

function install_prerequisites_yum {
	sudo nice yum -y update
	sudo nice yum -y upgrade
	sudo nice yum -y install libtool autoconf automake make gcc clang texinfo libusb libusb-devel libusb1 libusb1-devel libusbx libusbx-devel tcl-devel tcl pkgconfig libftdi wget
	#sudo nice yum -y install openocd # version is Open On-Chip Debugger 0.5.0 (2011-12-19-21:28) in SL6.10
	#sudo nice yum -y install openocd # version is Open On-Chip Debugger 0.8.0 (2014-04-29-12:22) in SL7.3 and SL7.5
	# for openocd-0.10.0 release tarball under redhat distros:
	# libusb-devel 0.1 needed to build ARM-OLIMEX-JTAG driver
	# libusb1-devel needed for SL6.10
	# libusbx-devel needed for SL7.5
	# ~2018 git version needs automake>=1.14 and SL7.3 only has 1.13 (SL7.5 has 1.13 also)
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
	git pull || /bin/true
else
	cd $build
	#if [ ! -e "openocd-0.10.0.tar.bz2" ]; then
	#	wget https://superb-sea2.dl.sourceforge.net/project/openocd/openocd/0.10.0/openocd-0.10.0.tar.bz2
	#fi
	#tar xjf openocd-0.10.0.tar.bz2
	#mv openocd-0.10.0 openocd
	git clone git://git.code.sf.net/p/openocd/code openocd
	#tar xf openocd-from-git-repo.tar
	cd $openocd
	if [ $redhat -gt 0 ]; then
		#find -type f -exec touch --reference=$build/openocd-patch2.tar.bz2 {} +
		find -exec touch --date="2018-11-28" {} + # must be older than the datestamps in the patch file below
		tar xjf $build/openocd-patch2.tar.bz2
		git submodule init
		git submodule update
	else
		nice ./bootstrap
	fi
fi

declare PREFIX="/usr"

cd $openocd
nice ./configure --prefix=$PREFIX --enable-ftdi --enable-buspirate --enable-ft232r --enable-armjtagew --enable-bcm2835gpio --disable-stlink --disable-ti-icdi --disable-ulink --disable-usb-blaster-2 --disable-vsllink --disable-xds110 --disable-osbdm --disable-opendous --disable-aice --disable-usbprog --disable-rlink --disable-cmsis-dap --disable-kitprog --disable-usb-blaster --disable-presto --disable-openjtag --disable-jlink --disable-parport --disable-parport-giveio --disable-jtag_vpi --disable-amtjtagaccel --disable-zy1000-master --disable-zy1000 --disable-ioutil --disable-ep93xx --disable-at91rm9200 --disable-imx_gpio --disable-gw16012 --disable-oocd_trace --disable-sysfsgpio --disable-werror

nice make
sudo nice make install

declare file="644" dir="755"
sudo find $PREFIX/share/openocd -type f -exec chmod --changes $file {} + -o -type d -exec chmod --changes $dir {} +
sudo cp -a $PREFIX/share/openocd/contrib/60-openocd.rules /etc/udev/rules.d/

ls -lart $PREFIX/bin/openocd $PREFIX/share/openocd /etc/udev/rules.d/60-openocd.rules

