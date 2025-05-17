import argparse
import subprocess
import sys
from typing import Optional

from image_manipulation import utils

default_size = 24
default_border = 30
default_orientation = "top-left-horizontal"

DIM_W = "w"


class ImageAnnotate:
    """
    Holds all the input and puts the text on the image in the correct location and orientation as requested.
    Also adds text to image metadata (EXIF). Runs Imagemagick to do the image manipulation.
    """

    def __init__(self, args: argparse.Namespace) -> None:
        self.text = args.text
        self.input_file = args.input_file
        self.output_file = args.output_file
        self.size = args.text_size
        self.border = args.border
        self.verbose = args.verbose
        self.horizontal = self.vertical = self.rotate_cmd = self.orientation = ""
        self.set_orientation(args.orientation)

    def set_orientation(self, orientation: str) -> None:
        self.orientation = orientation
        self.vertical, self.horizontal, direction = self.orientation.split("-")
        self.rotate_cmd = "" if direction in ("horizontal", "h") else "-rotate 90"

    @staticmethod
    def image_dimension(dim: str, file: str | None = None, stdin: Optional[bytes] = None) -> int:
        """
        Return horizontal or vertical size of given image file, or of the binary blob.
        Binary blob is a bytes object as used by `subprocess`.
        :param dim: 'h' or 'w' for height or width.
        :param file: File name, or '-' in order to use the binary blob in `stdin`.
        :param stdin: Optional text blob whose size is wanted.
        :return: The required dimension size in pixels.
        """
        w, h = utils.image_dimensions(file, stdin)
        if dim == DIM_W:
            return w
        else:
            return h

    def edge_distance(self, label: bytes, dim: str) -> int:
        """
        Returns distance from the edge given edge (dim) for the image.
        :param label: Image blob of the text to put on the image, as a bytes blob. This would come from Imagemagick.
        :param dim: 'h' or 'w' to get distance from top/bottom ('h') or left/right ('w').
        :return: Distance in pixels.
        """
        label_dim = self.image_dimension(dim, stdin=label)
        input_dim = self.image_dimension(dim, file=str(self.input_file))
        if input_dim < label_dim:
            print(f"WARN: {self.input_file} is too small for the text", file=sys.stderr)
        return input_dim - label_dim

    def labelimg(self) -> bytes:
        """
        Produces the text label as an image blob.
        :return: The bytes of the image blob.
        """
        args = (
            f"convert -density 100 -pointsize {str(self.size)}".split()
            + "-background #00000099 -fill white -gravity center -font Liberation-Serif".split()
            + [f"label: {self.text}"]
            + f"-strokewidth 8 {self.rotate_cmd} miff:-".split()
        )
        if self.verbose:
            print(args)
        return subprocess.run(args, capture_output=True, check=True).stdout

    def composite_cmd(self, label: bytes) -> list[str]:
        """
        Build the command to "composite" the text onto the base image in the correct place.
        :param label: Image bytes blob of the text to put on the image.
        :return: The Imagemagick command.
        """
        geometry_h = f"+{self.border}"
        if self.vertical in ("bottom", "b"):
            geometry_h = f'+{self.edge_distance(label, "h") - self.border}'
        elif self.vertical in ("middle", "m"):
            geometry_h = f'+{self.edge_distance(label, "h") // 2}'

        geometry_w = f"+{self.border}"
        if self.horizontal in ("right", "r"):
            geometry_w = f"+{self.edge_distance(label, DIM_W) - self.border}"
        elif self.horizontal in ("middle", "m"):
            geometry_w = f"+{self.edge_distance(label, DIM_W) // 2}"

        return (
            f"composite -compose atop -geometry {geometry_w}{geometry_h} -".split()
            + f"{self.input_file} {self.output_file}".split()
        )

    def exif_cmd(self) -> list[str]:
        """
        Builds commands to adjust image metadata according to various standards.
        :return: The exiv2 command.
        """
        return [
            "exiv2",
            f"-Mset Exif.Photo.UserComment charset=Ascii {self.text}",
            f"-Mset Iptc.Application2.Caption String {self.text}",
            f'-Mset Xmp.dc.description lang="x-default" {self.text}',
            self.output_file,
        ]

    def run(self) -> None:
        """Run commands to manipulate the image."""
        label = self.labelimg()
        composite_cmd = self.composite_cmd(label)

        if self.verbose:
            print("Composite Command:", " ".join(composite_cmd))
            print("EXIF Command:", " ".join(self.exif_cmd()))

        subprocess.run(composite_cmd, input=label, check=True)
        subprocess.run(self.exif_cmd())


def main() -> None:
    parser = argparse.ArgumentParser(description="Annotate image with text using ImageMagick and set EXIF metadata.")
    parser.add_argument("-t", "--text", required=True, help="Text to annotate image with")
    parser.add_argument("-i", "--input-file", required=True, help="Input image file")
    parser.add_argument("-o", "--output-file", required=True, help="Output image file")
    parser.add_argument(
        "-s", "--text-size", type=int, default=default_size, help=f"Font size (default: {default_size})"
    )
    parser.add_argument(
        "-b", "--border", type=int, default=30, help=f"Border size in pixels (default: {default_border})"
    )
    parser.add_argument(
        "-d",
        "--orientation",
        default=default_orientation,
        help=f"Orientation (default: {default_orientation}, see README for more options)",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")

    args = parser.parse_args()

    ImageAnnotate(args).run()


if __name__ == "__main__":
    main()
