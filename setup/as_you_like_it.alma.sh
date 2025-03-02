#!/bin/bash -e

# last updated 2025-02-21 by mza

function install_packages {
	local list=""
	#doublecmd-gtk
	nice sudo yum -y --enablerepo=extras install epel-release
	nice sudo yum -y update
	list="$list gvim vim meld svn git gpm nmap ImageMagick firefox hdparm screen tmux rsync mlocate openssh-server net-tools gnuplot zip unzip dbus-x11 iptables-services"
	list="$list gcc gcc-c++ make automake autoconf zip unzip nfs-utils ntfs-3g"
	list="$list dkms"
	list="$list kernel-devel"
	#list="$list yum-conf-virtualbox"
	#list="$list readline-devel zlib-devel bison-devel perl-Git-SVN mesa-libGLU-devel # for geant4"
	#list="$list dhcp xinetd tftp tftp-server policycoreutils-gui glibc.i686 redhat-lsb # for pocketdaq"
	#list="$list postgresql96-server postgresql96-contrib dhcp xinetd tftp tftp-server nfs-utils policycoreutils-gui glibc.i686 # for pocketdaq"
	#list="$list root pyserial hexedit # root - for cmake3 expat-devel"
	#list="$list mercurial qt5-qtdeclarative-devel dos2unix motif motif-static motif-devel libXpm-devel expat-devel libXmu-devel php-xml php-intl php-xcache php-mysql mariadb mariadb-server mediawiki123 mediawiki123-doc # for mediawiki"
	#list="$list texlive"
	#list="$list postfix telnet"
	#list="$list java vsftpd ftp"
	#list="$list python3 python34"
	#list="$list libftdi-devel libusb-devel"
	#list="$list clangp bison flex readline-devel"
	#list="$list tcl-devel"
	#list="$list apcupsd freeipmi-devel net-snmp-agent-libs net-snmp-devel libusb-devel"
	#list="$list kernel-devel gawk tcl-devel libffi-devel mercurial graphviz python-xdot pkgconfig python python3 libftdi-devel"
	#list="$list libtool clang texinfo libusb tcl-devel tcl pkgconfig libftdi # openocd"
	#list="$list VirtualBox-6.0 # host"
	#list="$list virtualbox-guest-utils virtualbox-guest-x11 virtualbox-guest-dkms # client"
	list="$list subversion mdadm wget fail2ban"
	nice sudo yum install -y $list
	nice sudo yum groupinstall -y "Development Tools"
	#echo "add the following line to /etc/ntp.conf:"
	#echo "	pool 192.168.153.1 iburst"
	#echo "and to set the local timezone:"
	#echo "	dpkg-reconfigure tzdata"
}

install_packages


