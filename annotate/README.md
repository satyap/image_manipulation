annotate
========


What
----

Put a text and EXIF caption on images, directly on the viewable image. Control the size, position, and orientation.

How
---

ruby annotate.rb -t "title/text of image" -i input\_file.jpg -o output\_file.jpg

Bottom right vertical placement of the text:
ruby annotate.rb -t "title/text of image" -i input\_file.jpg -o output\_file.jpg -d bottom-right-vertical

Use -s to specify the size in points:
ruby annotate.rb -t "title/text of image" -i input\_file.jpg -o output\_file.jpg -s 30

-d takes 3 words joined by dashes. The first position is top, middle, or bottom, the next is left, middle, or right, and the last is the orientation: horizontal or vertical. Examples:

top-left-horizontal
top-left-vertical
top-right-horizontal
top-right-horizontal
top-middle-vertical
top-middle-vertical
bottom-left-horizontal
bottom-left-vertical
bottom-right-horizontal
bottom-right-vertical
bottom-middle-horizontal
bottom-middle-vertical
middle-left-horizontal
middle-left-vertical
middle-right-horizontal
middle-right-horizontal
middle-middle-vertical
middle-middle-vertical


Why
---

ImageMagick command line syntax is dense, impenetrable, and very powerful. I
wrote a shellscript at first, and then I wanted to do more comlpicated things
from command-line options, so I did a Ruby script.


<a rel="license" href="http://creativecommons.org/licenses/by-sa/4.0/"><img alt="Creative Commons License" style="border-width:0" src="http://i.creativecommons.org/l/by-sa/4.0/88x31.png" /></a><br />This work is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by-sa/4.0/">Creative Commons Attribution-ShareAlike 4.0 International License</a>.
