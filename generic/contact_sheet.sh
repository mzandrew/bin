#!/bin/bash -e

# written 2023-05-14 by mza
# based on https://patdavid.net/2013/04/using-imagemagick-to-create-contact/
# last updated 2023-05-14 by mza

#nice montage -verbose -label '%f' -font Helvetica -pointsize 14 -background '#000000' -fill 'gray' -define jpeg:size=200x200 -geometry 200x200+2+2 -auto-orient *.[jJ][pP][gG] contact.jpeg
nice montage -label '%f' -font Helvetica -pointsize 14 -background '#000000' -fill 'gray' -define jpeg:size=200x200 -geometry 200x200+2+2 -tile 8x5 *.[jJ][pP][gG] contact.jpeg

