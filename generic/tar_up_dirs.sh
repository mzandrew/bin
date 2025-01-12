#!/bin/bash

# last updated 2025-01-12 by mza

declare temp_file="$(mktemp /tmp/datestamp.XXXXXX)"
declare local_dir=$(readlink -f "$(pwd)")
declare -i verbosity=3
if [ $verbosity -gt 3 ]; then echo "local_dir $local_dir"; fi
declare keep="--remove-files"

if [ "$1" == "-k" ]; then
	keep=""
	shift
fi

if [ $# -gt 0 ]; then
	for each; do
		each=$(echo "$each" | sed -e "s,/$,,g")
		if [ -e "$each" ]; then
			basename=$(basename "$each")
			if [ "$basename" == ".." ]; then continue; fi
			if [ "$basename" == "." ]; then continue; fi
			if [ $verbosity -gt 3 ]; then echo "basename $basename"; fi
			declare tar="${local_dir}/${basename}.tar"
			declare lfr="${local_dir}/${basename}.tar.lf-r"
			if [ $verbosity -gt 3 ]; then echo "tar $tar"; fi
			if [ $verbosity -gt 3 ]; then echo "lfr $lfr"; fi
			parent_dir=$(dirname "$each")
			parent_dir=$(readlink -f "$parent_dir")
			if [ $verbosity -gt 3 ]; then echo "parent_dir $parent_dir"; fi
			if [ -d "$parent_dir" ]; then
				cd "$parent_dir"
				if [ -d "$basename" ]; then
					if [ ! -e "$tar" ]; then
						echo "$basename"
						(
							cd "$basename"
							lf > "${lfr}"
						)
						touch --reference="$basename" "$temp_file"
						#tar cf "$tar" "$basename" --remove-files
						tar cf "$tar" "$basename" $keep
						touch --reference="$temp_file" "$tar"
						touch --reference="$temp_file" "$lfr"
						ls -lart "$tar" "$lfr"
					else
						echo "file \"${tar}\" already exists"
					fi
				fi
			fi
		fi
	done
else
	for each in * .*; do
		$0 "${each}"
	done
fi

rm -f "$temp_file"

