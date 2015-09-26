Image manipulation scripts
==========================

Shell, perl, and ruby scripts to put titles on images, fix aspect ratio, and create
title/subtitle images for use with `kdenlive` (or any non-linear video editor).

resize.pl
---------

I had a need to fit images into a 6x4 aspect ratio with white padding. This
perl script does it:

    resize.pl o_*.jpg

To add a 20-pixel border while we're at it:

    resize.pl 20 o_*.jpg

The original files need to be named `o_*`

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
