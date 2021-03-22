#!/bin/bash -e

for each; do
	exiftool -gps:all= $each
done

