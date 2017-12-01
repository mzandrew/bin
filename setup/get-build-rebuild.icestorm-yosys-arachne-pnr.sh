#!/bin/bash -e

# written 2017-11 by mza
# based on instructions posted at http://www.clifford.at/icestorm/
# last updated 2017-12-01

declare build="$HOME/build"
cd $build
if [ ! -e icestorm ]; then
	git clone https://github.com/cliffordwolf/icestorm.git icestorm
fi
if [ ! -e arachne-pnr ]; then
	git clone https://github.com/cseed/arachne-pnr.git arachne-pnr
fi
if [ ! -e yosys ]; then
	git clone https://github.com/cliffordwolf/yosys.git yosys
fi

function fix_permissions {
	sudo find ${@} -type d -exec chmod --changes 755 {} + -o -type f -exec chmod --changes 644 {} +
}

function fix_script_permissions {
	sudo find "${@}" -exec chmod --changes 755 {} +
}

# adapted from https://github.com/mzandrew/bin/blob/master/generic/lf
declare DATESTAMP='%TY-%Tm-%Td+%TH:%TM'
declare USERGROUP='%7u:%-7g'
declare PERMISSIONS='%M'
declare SIZE='%12s'
declare BASE="$DATESTAMP $USERGROUP $PERMISSIONS $SIZE %p"
declare REGULAR_FILE_STRING="$BASE\n"
declare REGULAR_DIR_STRING="$BASE/\n"
declare SYMLINK_STRING="$BASE -> %l\n"
function list_files {
	find "${@}" \
		-type d \( -name "proc" -o -name "dev" -o -name "\.svn" -o -name "\.git" \) -prune \
		-o -type d -printf "$REGULAR_DIR_STRING" \
		-o -type l -printf "$SYMLINK_STRING" \
		-o         -printf "$REGULAR_FILE_STRING" \
		| sort -k 1n,1
		
}

cd $build/icestorm
git pull
nice make
sudo nice make install
fix_permissions /usr/local/share/icebox
fix_script_permissions /usr/local/bin/ice*
#sudo chmod 755 /usr/local/bin/ice*
#sudo chmod 755 /usr/local/share/icebox
#sudo chmod 644 /usr/local/share/icebox/*
#list_files /usr/local/bin/ice* /usr/local/share/icebox

cd $build/arachne-pnr
git pull
nice make
sudo nice make install
fix_permissions /usr/local/share/arachne-pnr
fix_script_permissions /usr/local/bin/arachne*
#sudo chmod 755 /usr/local/bin/arachne*
#sudo chmod 755 /usr/local/share/arachne-pnr/
#sudo chmod 644 /usr/local/share/arachne-pnr/*
#list_files /usr/local/bin/arachne* /usr/local/share/arachne-pnr

cd $build/yosys
git pull
nice make
sudo nice make install
fix_permissions /usr/local/share/yosys/
fix_script_permissions /usr/local/bin/yosys*
#sudo chmod 755 /usr/local/bin/yosys*
#sudo chmod 755 /usr/local/share/yosys/
#sudo chmod 644 /usr/local/share/yosys/*
#list_files /usr/local/bin/yosys* /usr/local/share/yosys

echo; echo

list_files /usr/local/bin/ice* /usr/local/share/icebox /usr/local/bin/arachne* /usr/local/share/arachne-pnr /usr/local/bin/yosys* /usr/local/share/yosys

# yosys -p "synth_ice40 -blif rot.blif" rot.v
# arachne-pnr -d 1k -p rot.pcf rot.blif -o rot.asc
# icepack rot.asc rot.bin
# iceprog rot.bin
# sudo iceprog rot.bin

