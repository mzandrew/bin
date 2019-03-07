#!/bin/bash -e

# older: http://www.vspecialist.co.uk/2014/09/how-to-install-ipkg-on-a-synology-nas/
declare url="http://ipkg.nslu2-linux.org/optware-ng/bootstrap/buildroot-i686-bootstrap.sh"
declare dest="$HOME/build/optware-ng"

function install_packages {
	sudo ipkg update
	sudo ipkg install bc bzip2 coreutils diffutils file findutils gawk gcc git imagemagick python27 util-linux rsync openssh svn tmux mlocate xterm
}

function uninstall {
	sudo rm -rf /volume1/\@optware
	sudo rm -rf /volume2/\@optware
	sudo rm -rf /usr/lib/ipkg
	#echo "sudo vim /etc/rc.local # remove line for optware"
	echo "then reboot if you want to try to reinstall"
}

function installme {
	mkdir -p $dest
	cd $dest
	if [ ! -e buildroot-i686-bootstrap.sh ]; then
		wget $url
	fi
	sudo ./bootstrap.sh
}

mkdir -p build
installme

