#!/bin/bash -e

script="$(dirname $0)/extract-lf-listing-from-tar-file"
#echo "${script}"
find "${@}" -type f \( -iname "*.tar" -o -iname "*.tar.gz" -o -iname "*.tar.bzip2" -o -iname "*.tar.bz2" \) -exec ${script} {} +
#find -iname "*tar" -o -iname "*.tar.gz" -o -iname "*.tar.bzip2"

