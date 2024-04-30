#!/bin/bash -e

declare ttf_otf="${1}"
declare -i size="${2}"

declare basename=$(basename "${ttf_otf}")
declare bdf=$(echo $basename | sed -e "s,\.[ot]tf$,-${size}.bdf,")
declare pcf=$(echo $basename | sed -e "s,\.[ot]tf$,-${size}.pcf,")

if [ -e "${ttf_otf}" ]; then
	otf2bdf "${ttf_otf}" -p ${size} -o "${bdf}" || /bin/true
	bdftopcf "${bdf}" > "${pcf}"
fi

