#!/bin/bash -e

# written 2025-01-12 by mza
# following https://unix.stackexchange.com/a/406016/150012
# last updated 2025-01-24 by mza

# to get this script to run in massive parallel:
#find -type d -exec sh -c 'flac2mp3.sh "{}" &' \;

# to store the original flac files in a tar file (can optionally be removed later):
#find -type f -name "*.flac" -print0 | tar cf flac.tar --remove-files --null -T -

if [ $# -gt 0 ]; then
	for each; do
		find "$each" -type f -name "*.flac" -exec sh -ce '
			for in; do
				out=$(echo "$in" | sed -e "s,\.flac$,.mp3,");
				if [ ! -e "$out" ]; then
					echo "$in"
					ffmpeg -i "$in" -ab 320k -map_metadata 0 -id3v2_version 3 "$out" >/dev/null 2>&1
					touch --reference="$in" "$out"
					rm -v "$in"
				fi
			done
		' sh {} +
	done
else
	find . -type f -exec $0 "{}" +
fi

