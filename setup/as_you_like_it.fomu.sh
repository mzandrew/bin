#!/bin/bash -e

# last updated 2019-08-21 by mza

function install_prerequisites_apt {
	sudo nice apt -y install ruby ruby-dev make gcc libcurl3 autoconf libz-dev ruby-bundler
}

function install_prerequisites_yum {
	sudo nice yum -y update
	sudo nice yum -y upgrade
}

function install_prerequisites_pac {
	sudo pacman --needed --noconfirm -Syu
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
declare fomu="${build}/fomu-workshop"
mkdir -p "$build"

#cd "$build"
#if [ ! -e "$fomu" ]; then
#	git clone https://github.com/im-tomu/fomu.im.git
#fi
#cd "$fomu"
#bundle install --path vendor/bundle
#bundle exec jekyll serve

cd "$build"
if [ ! -e "$fomu" ]; then
	git clone https://github.com/im-tomu/fomu-workshop.git
fi
cd "$fomu"

#git clone https://github.com/im-tomu/foboot.git
#git clone https://github.com/im-tomu/fomu-hardware.git

