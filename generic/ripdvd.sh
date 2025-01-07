#!/bin/bash -e

# following https://gist.github.com/andreasbotsikas/8bad3df5309dd0383f2e2c450b22481c
intermediate_file="${HOME}/bigfile.vob"

if [ -e VTS_01_7.VOB ]; then
	cat VTS_01_1.VOB VTS_01_2.VOB VTS_01_3.VOB VTS_01_4.VOB VTS_01_5.VOB VTS_01_6.VOB VTS_01_7.VOB > ${intermediate_file}
elif [ -e VTS_01_6.VOB ]; then
	cat VTS_01_1.VOB VTS_01_2.VOB VTS_01_3.VOB VTS_01_4.VOB VTS_01_5.VOB VTS_01_6.VOB > ${intermediate_file}
elif [ -e VTS_01_5.VOB ]; then
	cat VTS_01_1.VOB VTS_01_2.VOB VTS_01_3.VOB VTS_01_4.VOB VTS_01_5.VOB > ${intermediate_file}
elif [ -e VTS_01_4.VOB ]; then
	cat VTS_01_1.VOB VTS_01_2.VOB VTS_01_3.VOB VTS_01_4.VOB > ${intermediate_file}
elif [ -e VTS_01_3.VOB ]; then
	cat VTS_01_1.VOB VTS_01_2.VOB VTS_01_3.VOB > ${intermediate_file}
elif [ -e VTS_01_2.VOB ]; then
	cat VTS_01_1.VOB VTS_01_2.VOB > ${intermediate_file}
else
	cat VTS_01_1.VOB > ${intermediate_file}
fi

#ffmpeg -loglevel warning -i "${intermediate_file}" -codec:a copy -codec:v libx264 "/opt/zdog/video/output.mp4"
#ffmpeg -i "${intermediate_file}" -codec:a ac3 -codec:v libx264 "ConCat.mp4"
#rm -f "${intermediate_file}"

#ffmpeg -i concat:VTS_01_1.VOB\|VTS_01_2.VOB\|VTS_01_3.VOB\|VTS_01_4.VOB \
#-map 0:0 -map 0:1 -map 0:2 -map 0:6 -map 0:5 -map 0:4 \
#-c:v libx264 -preset fast -crf 18 \
#-c:a copy -metadata:s:a:0 language=ger \
#-c:a copy -metadata:s:a:1 language=eng \
#-c:s copy -metadata:s:s:0 language=eng \
#-c:s copy -metadata:s:s:1 language=ger \
#-c:s copy -metadata:s:s:2 language=ger \
#-f matroska movie.mkv 

