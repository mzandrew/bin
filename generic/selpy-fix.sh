#!/bin/bash -e

for each in *.jpg; do
	convert -interlace none $each $each
	convert $each -thumbnail '196x196>' ${each}.thumb
	exiftool "-ThumbnailImage<=${each}.thumb" -P -overwrite_original $each
	rm ${each}.thumb
done

