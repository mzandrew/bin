#!/bin/bash -e

declare a="${1}"
declare b="${2}"
declare -i size_a size_b

cd "${a}"
for each in *; do
	if [ -e "$each" ]; then
		size_a=$(du --ma=0 --block-size=1000000 "$each"      | awk '{ print $1 }');
	fi
	if [ -e "${b}/$each" ]; then
		size_b=$(du --ma=0 --block-size=1000000 "${b}/$each" | awk '{ print $1 }');
		diff=$((size_a-size_b));
		echo "$diff = $size_a - $size_b $each";
	else
		echo "$each exists in $a but not $b"
	fi
done | sort -n

