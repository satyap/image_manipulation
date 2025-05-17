# Image Manipulation Scripts

A collection of Python and shell scripts for:

* Adding titles or descriptions to images
* Fixing image aspect ratios for printing
* Generating title/subtitle cards for video editors like `kdenlive`

⚠️ Make backup copies of your images before using these scripts. Many will overwrite files.

## Installation

These tools use ImageMagick via its command-line interface (CLI). Make sure it’s installed and accessible via your system `PATH`.

To install the Python commands:
```commandline
pip install .
```

## Resize images to a fixed aspect ratio

This tool pads images to match a target aspect ratio (default: 4x6). It overwrites files by default.

Resize all .jpg images to 6×4 (or 4×6, depending on image orientation):

```commandline
ima-resize *.jpg
```

Add a 20-pixel border before resizing:
```commandline
ima-resize -b 20 *.jpg
```
You can also set a different target ratio using -r:

```commandline
ima-resize -r 5x7 *.jpg
```
Supported ratios: `4x6`, `5x7`, `8x10`, `11x14`.

## Create video title and subtitle cards

The shell scripts `mksub.sh` and `mktitle.sh` generate PNG title/subtitle cards for use in kdenlive or other video editors.

Usage is built into the scripts—open them for details.

## Annotate images with text and metadata

Automatically generate `ima-annotate` commands based on image dates:

```bash
ima-mkpics -p prefix *.jpg > commands.sh
```

This will:

* Extract the image date from EXIF metadata or (for WhatsApp images) from the filename
* Generate shell commands to annotate each image and optionally create XML metadata
* Output a script `t.sh` that you can edit and run

To apply annotations:

```commandline
sh commands.sh
```

Output files are named based on the image’s timestamp and prefixed with the `-p` argument (`prefix`).

Use `-x` to also generate .xml metadata files:

```bash
ima-mkpics -x -p myprefix *.jpg > commands.sh
```

See help for all options:

```commandline
ima-mkpics -h
ima-annotate -h
```

### Annotation Position Format (`-d` flag)

The `-d` (direction) flag controls text placement. It takes a hyphenated combination of:

* Vertical position: top, middle, bottom
* Horizontal position: left, middle, right
* Orientation: horizontal, vertical

Examples:
```text
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
```

You can abbreviate using first letters, e.g. `t-l-h` = `top-left-horizontal`.
