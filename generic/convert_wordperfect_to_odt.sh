#!/bin/bash -e

# sudo apt install -y wpd2odt

# written 2022-04-03 by mza

if [ $# -gt 0 ] ;then
	for each; do
		#if [ "${each}" == "." ]; then continue; fi
		#if [ "${each}" == ".." ]; then continue; fi
		if [ "${each: -3}" == "odt" ]; then continue; fi
		if [ -e "${each}" ]; then
			if [ -d "${each}" ]; then
				#find "$each" -exec $0 "{}" +
				continue
			fi
			#new="$(basename "$each").odt"
			new="${each}.odt"
			if [ ! -e "${each}.odt" ]; then
				echo "$each"
				wpd2odt "${each}" > "${new}" && touch --reference="$each" "${new}" || rm "${new}" && file "${each}"
			fi
		else
			echo "can't find file $each"
		fi
	done
else
	find . -exec $0 "{}" +
fi

