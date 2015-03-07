Image manipulation scripts
==========================

Shell and ruby scripts to put titles on images, fix aspect ratio, and create
title/subtitle images for use with `kdenlive` (or any non-linear video editor).

resize.pl
=========

I had a need to fit images into a 6x4 aspect ratio with white padding. This perl script does it:

    resize.pl o_*.jpg

To add a 20-pixel border while we're at it:

    resize.pl 20 o_*.jpg

The original files need to be named `o_*`

mksub.sh and mktitle.sh
=======================

Creates a subtitle or title image that can be used with `kdenlive`. See the script for usage.
