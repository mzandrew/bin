#!/bin/bash -e

# written 2020-06 by mza
# last updated 2020-08-26 by mza

# https://superuser.com/a/598696/539022
function run {
	local dir="${@}"
	if [ -e "${dir}" ] && [ -d "${dir}" ]; then
		find "${dir}" -maxdepth 1 -type f -iname "*.jpg" -o -iname "*.jpeg" | while read each; do
			echo "$each"
			convert -interlace none $each $each
			convert $each -thumbnail '196x196>' ${each}.thumb
			exiftool "-ThumbnailImage<=${each}.thumb" -P -overwrite_original $each
			rm ${each}.thumb
			# fix datestamp with exif data
			# ...
			# must be named .jpg, not .jpeg:
#			if [ "${each: -4}" == "jpeg" ]; then
#				mv "$each" "$new"
#			fi
		done
	fi
}

# https://superuser.com/a/1070947/539022
if [ $# -gt 0 ]; then
	for each; do
		run "$each"
	done
else
	find . -type d -name "lowres" -prune -o -type d -exec $0 "{}" \;
	#find . -type d -name "lowres" -prune -o -type d -print
fi

