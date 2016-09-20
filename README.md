Image manipulation scripts
==========================

Shell, perl, and ruby scripts to put titles on images, fix aspect ratio, and create
title/subtitle images for use with `kdenlive` (or any non-linear video editor).

Please make backup copies of your files before using these scripts.

resize.pl
---------

This will overwrite the files given to it, so make backups.

I had a need to fit images into a 6x4 aspect ratio with white padding. This
perl script does it:

    resize.pl *.jpg

To add a 20-pixel border while we're at it:

    resize.pl 20 *.jpg

To add a border using imagemagick:

    for r in *;do convert $r -bordercolor white -border 60x40 new_$r;done

mksub.sh and mktitle.sh
-----------------------

Creates a subtitle or title image that can be used with `kdenlive`. See the
script for usage.

mkpics.pl
---------

Uses EXIF data to create commands to annotate, and to create `bins` meta-data
files. Uses the `annotate/annotate.rb` script.

titler.rb
---------

Advanced usage.

    ruby titler.rb 3 *.png

Prints out title clip tags suitable for KDEnlive's saved file format. The first
argument should be the starting numeric ID. Paste the result into the save file
in the appropriate place.
