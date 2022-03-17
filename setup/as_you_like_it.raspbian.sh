#!/bin/bash -e

declare -i MiB=1024

function add_swap_if_necessary {
	if [ ! -e /swap ]; then
		echo "generating $MiB MiB /swap file..."
		sudo dd if=/dev/zero of=/swap bs=$((1024*1024)) count=$MiB
		sudo chmod 600 /swap
		sudo mkswap /swap
		sudo swapon /swap
		# this happens after the "exit 0" line, so is useless:
		#sudo sed -ie '/swapon/{h;s/.*/swapon \/swap/};${x;/^$/{s/.*/swapon \/swap/;H};x}' /etc/rc.local
		echo "fix /etc/rc.local to do \"swapon /swap\" before the exit 0!"
	fi
}

function install_packages_0 {
	sudo apt -y install vim git ntp
	#sudo sed -i "s/gb/us/" /etc/default/keyboard
	sudo raspi-config # enable sshd; change video memory to 16MB; change hostname; enable spi+i2c+1wire
}

function install_packages_1 {
	sudo apt-get clean
	sudo apt -y install mlocate subversion rsync
	sudo apt -y update
	sudo apt -y upgrade
	sudo apt -y install firefox-esr nfs-common tmux
#	sudo apt -y install network-manager-openconnect-gnome # for VPN
	sudo apt -y install libcanberra-gtk-module libcanberra-gtk3-module # to avoid annoying messages
	sudo apt -y install vim-gtk cmake imagemagick eog
	sudo apt-get -y autoremove
	sudo apt-get clean
}

function install_packages_2 {
	sudo apt install -y raspinfo rpi.gpio-common raspi-gpio python-rpi.gpio python3-rpi.gpio python3-gpiozero python-gpiozero python3-spidev python-spidev i2c-tools spi-tools python3-picamera python-picamera u-boot-rpi rpiboot lm-sensors lshw wiringpi libpigpio-dev pigpio-tools python-pigpio python3-pigpio # rpi-specific
	# rpi-chromium-mods # includes flash player
	#sudo apt install mpd mpc easytag audacious # audio stuff
	# python3-pychrome mkchromecast castpulseaudio-dlna
	#sudo apt install lightdm raspberrypi-ui-mods # gui on top of rasbpian lite
	sudo apt install -y python3-pip
	#sudo pip3 install numpy
	#sudo pip3 install opencv-python
}

function install_packages_3 {
	# https://www.raspberrypi.org/forums/viewtopic.php?t=133691
	sudo apt install -y xserver-xorg xinit
	#sudo apt install -y raspberrypi-ui-mods lxsession
	sudo apt install -y lxde-core lxappearance
	#sudo apt install -y xfce4 xfce4-terminal
	#sudo apt install -y mate-desktop-environment-core
	sudo apt install -y lightdm
	sudo apt install -y mplayer vlc kodi ffmpeg
}

#sudo useradd mza
#sudo usermod mza -a -G sudo

install_packages_0
# reboot, and continue:
install_packages_1
install_packages_2

#add_swap_if_necessary

