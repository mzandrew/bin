#!/bin/bash

declare temp_file="$(mktemp /tmp/datestamp.XXXXXX)"

for each in * .*; do
	declare tar="${each}.tar"
	declare lfr="${tar}.lf-r"
	if [ "$each" == ".." ]; then continue; fi
	if [ "$each" == "." ]; then continue; fi
	#echo "$each"
	if [ -d "$each" ]; then
		if [ ! -e "$tar" ]; then
			echo "$each"
			(
				cd "$each"
				lf > "../${lfr}"
			)
			touch --reference="$each" "$temp_file"
			tar cf "$tar" "$each" --remove-files
			touch --reference="$temp_file" "$tar"
			touch --reference="$temp_file" "$lfr"
			ls -lart "$tar" "$lfr"
		else
			echo "file \"${tar}\" already exists"
		fi
	fi
done
rm "$temp_file"

