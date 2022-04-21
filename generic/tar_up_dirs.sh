#!/bin/bash

declare temp_file="$(mktemp /tmp/datestamp.XXXXXX)"

if [ $# -gt 0 ]; then
	for each; do
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
else
	for each in * .*; do
		$0 "${each}"
	done
fi

rm -f "$temp_file"

