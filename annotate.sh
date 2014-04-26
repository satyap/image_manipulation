# Shellscript, obsolete, beacuse why not.
#qual=$4
#[ "$qual" == "" ] && qual=70
size=$4
if [ "$size" = "" ]
then size=20
fi

# convert -list font | grep -i times|grep Font:

convert -density 100 -pointsize $size -background '#00000099' -fill white \
-gravity center \
-font Times-New-Roman-Bold \
label:" $1 " \
-strokewidth 8 \
miff:-| \
composite -compose atop -geometry "+30""+30" - "$2" $3

#convert $3 -set caption "$1" \
#-set comment "$1" \
#-set label "$1" \
#$3

exiv2 \
    -M"set Exif.Photo.UserComment charset=Ascii $1" \
    -M"set Iptc.Application2.Caption String $1" \
    -M"set Xmp.dc.description lang=\"x-default\"  $1" \
    mo $3

#-geometry "+13""+20" \
echo $2 pointsize $size
#convert $2 -box '#00000066' \
#-fill '#00000066' -border "-15" \
#-pointsize 18 -fill white -font Helvetica \
#-gravity NorthWest -annotate "+10+10" " $1" $3

#echo Quality: $qual
