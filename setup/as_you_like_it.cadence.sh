#!/bin/bash -e

# last updated 2018-12-31 by mza

function install_prerequisites_apt {
	# from list posted at https://support.cadence.com/apex/ArticleAttachmentPortal?id=a1O0V000007MpXKUA0&pageName=ArticleContent&sq=005d0000001T5YzAAK_2017899185859
	sudo nice apt -y install core build-essential ksh ldap-utils lib32bz2-1.0 lib32ncurses5 lib32z1 libgl1-mesa-dri libgl1-mesa-glx libglu1-mesa libxss1 libc6-dev-i386 nfs-kernel-server ubuntu-desktop xvfb kde-standard sqlite3 xutils-dev
}

function install_prerequisites_yum {
	# from instructions posted at https://www.phys.hawaii.edu/~mza/ASIC/Cadence/cadence.html
	sudo nice yum -y update
	sudo nice yum -y upgrade
	sudo nice yum -y install java nfs-utils xauth vim-enhanced gvim firefox
	sudo yum -y install ksh glibc.i686 glibc-devel.i686 libXext.i686 libXtst.i686 libXt.i686 mesa-libGL.i686 mesa-libGL.i686 libXft.so.2 libXp.so.6 libXp.x86_64 xorg-x11-fonts-100dpi xorg-x11-fonts-75dpi xorg-x11-fonts-misc libXScrnSaver
	if [ $CENT7 -gt 0 ]; then
		sudo yum -y install elfutils-libelf.i686 redhat-lsb redhat-lsb.i686 mesa-libGLU.i686 motif motif.i686 libpng.i686 libjpeg-turbo.i686 glibc-devel
	fi
}

function install_prerequisites_pac {
	sudo pacman --needed --noconfirm -Syu
	#sudo pacman --needed --noconfirm -S 
}

declare -i redhat=0 CENT6=0 CENT7=0 SL5=0 SL6=0 SL7=0 deb=0
if [ -e /etc/redhat-release ]; then
	redhat=1
	#set +e
	CENT6=$(grep -c "CentOS release 6" /etc/redhat-release)
	CENT7=$(grep -c "CentOS Linux release 7" /etc/redhat-release)
	SL5=$(grep -c "Scientific Linux release 5" /etc/redhat-release)
	SL6=$(grep -c "Scientific Linux release 6" /etc/redhat-release)
	SL7=$(grep -c "Scientific Linux release 7" /etc/redhat-release)
	#set -e
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

sudo systemctl enable sshd
sudo systemctl start sshd
sudo chkconfig wpa_supplicant off
sudo chkconfig bluetooth off
sudo chkconfig autofs off
sudo useradd -m asic --user-group

#declare PREFIX="/opt/cadence"

echo
echo "for each new user, do:"
echo "usermod --append --groups asic USERNAME"
