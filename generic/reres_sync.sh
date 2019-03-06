#!/bin/bash -e

# written 2018-06-24 by mza
# last updated 2019-03-06 by mza

# this version runs at about 6 images/sec when just checking them (all conversions already done); 208 images + 4 mov in 35.5 seconds

#declare res
#res="1600x1200" # takes 160 seconds to convert 208 images
#res="1920x1080" # takes 131 seconds to convert 208 images
#res="2560x1440" # takes 159 seconds to convert 208 images
#res="3840x2160" # takes 108 seconds to convert 208 images
#declare string="-resize ${res}>" # > = only make smaller; never enlarge

declare megapixels=2.0
declare -i pixels=$(echo "$megapixels*1000000/1" | bc)
declare string="-resize ${pixels}@>" # > = only make smaller; never enlarge
#echo "$string"

if [ $# -lt 2 ]; then
	echo "usage:"
	echo "$0 source destination"
	exit 1
fi

declare source="$1"
declare destination="$2"

if [ ! -e "$source" ]; then
	echo "$source does not exist"
	exit 2
fi

if [ ! -e "$destination" ]; then
	mkdir -p "$destination"
	#chown "$destination" --reference="$source"
fi

function doit {
	local sfile="${1}"
	local dfile="${2}"
	set +e
	nice convert "$sfile" $string "$dfile"
	if [ $? -eq 0 ]; then
		touch "$dfile" --reference="$sfile"
	else
		echo "error with \"$sfile\""
		rm -f "$dfile"
	fi
	set -e
}

declare -i total=0 converted_this_time=0 already_converted=0 unknown_type=0
find "$source" -type d \( -name "@eaDir" -o -name ".xvpics" \) -prune -o -type f -print | while read sfile; do
	total=$((total+1))
#echo $total
	if [ -e "$sfile" ]; then
		filename=$(basename "$sfile")
		ext=$(echo "$filename" | sed -e "s,.*\.\([^\.]*\),\1," | tr 'A-Z' 'a-z')
		if [ ! "$ext" = "jpg" ] && [ ! "$ext" = "jpeg" ] && [ ! "$ext" = "png" ]; then
			#echo "not handling file $sfile"
			unknown_type=$((unknown_type+1))
			continue
		fi
		dir=$(dirname "$sfile" | sed -e "s,^$source,,")
		dir=$(echo "$dir" | sed -e "s,^/,,")
		if [ "$dir" = "" ]; then
			ddir="$destination"
		else
			ddir="$destination/$dir"
		fi
		#dir=$(echo "$dir" | sed -e "s,/$,,")
		dfile="$ddir/$filename"
		if [ -e "$dfile" ]; then
			if [ "$sfile" -nt "$dfile" ]; then
				echo "re-generating $dfile..."
				doit "$sfile" "$dfile"
				converted_this_time=$((converted_this_time+1))
			else
				already_converted=$((already_converted+1))
			fi
		else
			if [ ! -e "$ddir" ]; then
				echo "creating dir $ddir..."
				mkdir -p "$ddir"
			fi
			echo "generating $dfile..."
			doit "$sfile" "$dfile"
			converted_this_time=$((converted_this_time+1))
		fi
	fi
done

#the above is done in a subshell, so these counts are zero here:
#echo "      total file(s): $total"
#echo "converted this time: $converted_this_time"

