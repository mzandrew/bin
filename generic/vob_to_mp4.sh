#!/bin/bash -e

declare input="${1}"
declare output="$(echo $input | sed -e "s,\.vob$,.mp4,i")"

ffmpeg -threads 32 -i "${input}" -vf yadif -c:v libx264 -preset slow -crf 19 -c:a aac -b:a 256k "${output}"

