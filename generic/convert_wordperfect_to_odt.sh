#!/bin/bash

# written 2022-04-03 by mza
# last updated 2022-04-06 by mza

which wpd2odt >/dev/null
if [ $? -ne 0 ]; then
	echo "wpd2odt required.  try:\nsudo apt install -y wpd2odt"
	exit
fi

declare originals_tar="originals.tar"

function run_on_file {
	local each="${1}"
	#echo "found file \"${each}\""
	#if [ "${each}" == "." ]; then continue; fi
	#if [ "${each}" == ".." ]; then continue; fi
	if [ "${each: -4}" == ".odt" ]; then return; fi
	if [ "${each: -4}" == ".tar" ]; then return; fi
	local is_wordperfect_file=0
	local new="${each}.odt"
	if [ ! -e "${each}.odt" ]; then
		is_wordperfect_file=$(file "${each}" | grep -ci wordperfect)
		if [ $is_wordperfect_file -gt 0 ]; then
			echo "${each}"
			wpd2odt "${each}" "${new}"
			if [ $? -ne 0 ]; then
				rm -f "${new}"
				file "${each}"
			else
				touch --reference="$each" "${new}"
				(
					local dirname="$(dirname "${each}")"
					local basename="$(basename "${each}")"
					#echo "$dirname $basename"
					cd "$dirname"
					tar rf "${originals_tar}" "${basename}" --remove-files
				)
			fi
		fi
	fi
}

function run_on_dir {
	local each="${1}"
	#echo "found dir \"${each}\""
	find "$each" -type f -exec $0 "{}" +
}

if [ $# -gt 0 ] ;then
	for each; do
		if [ -e "${each}" ]; then
			if [ -d "${each}" ]; then
				run_on_dir "${each}"
			elif [ -L "${each}" ]; then
				echo "ignoring symlink"
			else
				run_on_file "${each}"
			fi
		else
			echo "can't find \"$each\""
		fi
	done
else
	find . -type f -exec $0 "{}" +
fi

