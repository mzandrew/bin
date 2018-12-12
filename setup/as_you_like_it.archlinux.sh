#!/bin/bash -e

cd
for each in Downloads/ Desktop/ Videos/ Templates/ Public/ Music/ Documents/ Pictures/; do
	if [ -e $each ]; then
		rmdir $each
	fi
done

cd
mkdir -p build # for development

cd
if [ ! -e build ]; then
	cd build
	if [ ! -e bin ]; then
		git clone https://github.com/mzandrew/bin.git
	fi
fi

cd
if [ ! -e bin ]; then
	mkdir -p bin
	cd bin
	ln -s ../build/bin/generic
fi

cd
cat >> .bashrc <<HERE
if [ -e $HOME/build/bin/nofizbin/bashrc ]; then
	. $HOME/build/bin/nofizbin/bashrc
fi
HERE

cd
mkdir -p tmp # for vim swap files

cd
if [ ! -e .vimrc ]; then
	ln -s build/bin/nofizbin/.vimrc
fi

which git 2>&1 > /dev/null
if [ $? -eq 0 ]; then
	git config --global user.name mzandrew
	echo "git config --global user.email blah@org"
	#git config --global push.default simple
fi

sudo pacman --needed --noconfirm -Syu
sudo pacman --needed --noconfirm -S gvim firefox imagemagick git openssh rsync subversion wget zip mlocate gpm xterm

