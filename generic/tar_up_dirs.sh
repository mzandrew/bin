#!/bin/bash

declare temp_file="$(mktemp /tmp/datestamp.XXXXXX)"

for each in * .*; do
	declare tar="${each}.tar"
	if [ "$each" == ".." ]; then continue; fi
	if [ "$each" == "." ]; then continue; fi
	#echo "$each"
	if [ -d "$each" ]; then
		if [ ! -e "$tar" ]; then
			echo $each
			touch --reference="$each" "$temp_file"
			tar cf "$tar" "$each" --remove-files
			touch --reference="$temp_file" "$tar"
			ls -lart "$tar"
		else
			echo "file \"${tar}\" already exists"
		fi
	fi
done
rm "$temp_file"

