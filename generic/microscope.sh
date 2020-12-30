#!/bin/bash -e

# written 2020-11-16 by mza
# last updated 2020-11-18 by mza

declare destination="$HOME/microscope"
mkdir -p "$destination"
declare original="picture.jpeg"
declare tmpfile="$(mktemp /tmp/microscope.XXXXXX)"

function find_and_rename_new_images {
	cd "$destination"
	while /bin/true; do
		if [ -e "$original" ]; then
			local datestamp=$(date +"%Y-%m-%d+%H%M%S")
			sleep 0.25
			mv "$original" "${datestamp}.jpeg"
			ls -lart "${datestamp}.jpeg"
		fi
		sleep 0.25
		if [ ! -e "$tmpfile" ]; then
			#echo "quitting background process"
			exit 0
		fi
	done
}

find_and_rename_new_images &

cd "$destination"
echo "ENTER to take/retake image"
echo "x ENTER to quit"
echo
raspistill --fullscreen --timeout 0 --vflip --hflip -awb sun --preview 0,0,1920,1080 -k -o "$original"
rm "$tmpfile"
sleep 0.5

