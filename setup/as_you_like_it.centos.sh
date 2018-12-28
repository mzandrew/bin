#!/bin/bash -e

function install_packages {
	#doublecmd-gtk
	#sudo yum -y install yum-conf-virtualbox
	sudo yum --enablerepo=extras install epel-release
	sudo yum -y update
	sudo yum -y install gvim vim meld svn git gpm nmap ImageMagick firefox hdparm screen tmux rsync mlocate openssh-server net-tools gnuplot zip unzip dbus-x11 iptables-services
	sudo yum -y install yum-cron redhat-lsb gcc gcc-c++ make automake autoconf zip unzip
	sudo yum -y install dkms
	sudo yum -y groupinstall "Development Tools"
	sudo yum -y install kernel-devel
	#sudo yum -y install readline-devel zlib-devel bison-devel perl-Git-SVN mesa-libGLU-devel # for geant4
	#sudo yum -y install ntp dhcp xinetd tftp tftp-server nfs-utils policycoreutils-gui glibc.i686 redhat-lsb # for pocketdaq
	#sudo yum -y install postgresql96-server postgresql96-contrib dhcp xinetd tftp tftp-server nfs-utils policycoreutils-gui glibc.i686 # for pocketdaq
	#sudo yum -y install root pyserial hexedit # root - for cmake3 expat-devel
	#sudo yum -y install mercurial qt5-qtdeclarative-devel dos2unix motif motif-static motif-devel libXpm-devel expat-devel libXmu-devel php-xml php-intl php-xcache php-mysql mariadb mariadb-server mediawiki123 mediawiki123-doc # for mediawiki
	#sudo yum -y install texlive
	#sudo yum -y install postfix telnet
	#sudo yum -y install java vsftpd ftp
	#sudo yum -y install python3 python34
	#sudo yum -y install libftdi-devel libusb-devel
	#sudo yum -y install clangp bison flex readline-devel
	#sudo yum -y install tcl-devel
	#sudo yum -y install apcupsd freeipmi-devel net-snmp-agent-libs net-snmp-devel libusb-devel
	#sudo yum -y install kernel-devel gawk tcl-devel libffi-devel mercurial graphviz python-xdot pkgconfig python python3 libftdi-devel
	#sudo yum -y install libtool clang texinfo libusb tcl-devel tcl pkgconfig libftdi # openocd
	#sudo yum -y install VirtualBox-6.0 # host
	#sudo yum -y install virtualbox-guest-utils virtualbox-guest-x11 virtualbox-guest-dkms # client
	#echo "consider switching to use the local epel mirror:"
	#echo "  http://mirror.ancl.hawaii.edu/linux/epel"
	#echo "	sudo sed -i 's,us.archive.ubuntu.com,mirror.ancl.hawaii.edu/linux,' /etc/apt/sources.list"
	#echo "	sudo sed -i 's,archive.ubuntu.com,mirror.ancl.hawaii.edu/linux,' /etc/apt/sources.list"
	echo "add the following line to /etc/ntp.conf:"
	echo "	pool 192.168.153.1 iburst"
	echo "and to set the local timezone:"
	echo "	dpkg-reconfigure tzdata"
}

install_packages
exit

cd
mkdir -p build

if [ ! -e ~/build/bin ];then
	cd ~/build
	git clone https://github.com/mzandrew/bin.git
fi

cd
mkdir -p bin

cd ~/bin
if [ ! -e generic ]; then ln -s ../build/bin/generic; fi
if [ ! -e setup   ]; then ln -s ../build/bin/setup; fi
if [ ! -e repo    ]; then ln -s ../build/bin/repo; fi
if [ ! -e physics ]; then ln -s ../build/bin/physics; fi

cat >> ~/.bashrc <<HERE

if [ -e $HOME/build/bin/nofizbin/bashrc ]; then
	. $HOME/build/bin/nofizbin/bashrc
fi

HERE

