#!/bin/bash -e

if [ $# -eq 0 ]; then
	find . -type f -iname "*.tar" -exec bzip2 -v {} \;
else
	for each; do
		find "${each}" -type f -iname "*.tar" -exec bzip2 -v {} \;
	done
fi

