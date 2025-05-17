import argparse
import logging
import subprocess
import tempfile
import shutil
import os
from typing import Tuple

from image_manipulation import utils

logging.basicConfig(level=logging.INFO)


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Pad images to a fixed aspect ratio using ImageMagick CLI (overwrites by default)."
    )
    parser.add_argument(
        "-b", "--border", type=int, default=0, help="Border size to apply before aspect ratio correction (default: 0)."
    )
    parser.add_argument(
        "-d", "--dry-run", action="store_true", help="Show what would be done without modifying any files."
    )
    parser.add_argument("-q", "--quiet", action="store_true", help="Don't log what we're doing")
    parser.add_argument(
        "-r",
        "--ratio",
        choices=["4x6", "5x7", "8x10", "11x14"],
        default="4x6",
        help="Aspect ratio to use for resizing (default: 4x6). The script automatically adjusts the orientation.",
    )
    parser.add_argument("images", nargs="+", help="Image files to process")
    return parser.parse_args()


def calculate_ratio_from_arg(ratio_str: str) -> float:
    """Calculate the base aspect ratio from a string like '4x6'. Assumes portrait orientation by default."""
    return {
        "4x6": 4 / 6,
        "5x7": 5 / 7,
        "8x10": 8 / 10,
        "11x14": 11 / 14,
    }.get(
        ratio_str, 4 / 6
    )  # Default to 4x6 if not found


def fix_ratio(w: int, h: int, ratio_key: str) -> Tuple[int, int]:
    """
    Adjust image dimensions to match a target aspect ratio.

    Automatically adjusts for orientation:
    - Uses portrait ratio if height > width
    - Inverts the ratio for landscape images

    :param w: Width including border
    :param h: Height including border
    :param ratio_key: Aspect ratio key, e.g., '4x6'
    :return: Tuple of (new_width, new_height)
    """
    ratio = calculate_ratio_from_arg(ratio_key)
    if w > h:  # wide image
        ratio = 1 / ratio
    actual = w / h
    logging.info(f"Target ratio: {ratio:.4f}, actual: {actual:.4f}")
    if actual > ratio:
        return w, int(round(w / ratio))
    else:
        return int(round(h * ratio)), h


def process_image(path: str, border: int, dry_run: bool, ratio: str) -> None:
    """
    Process a single image:
    - Compute padded dimensions
    - Resize if needed

    :param ratio: desired aspect ratio
    :param path: Path to the image file
    :param border: Border size to apply before ratio check
    :param dry_run: If True, only simulate the changes
    """
    logging.info(f"*** Processing: {path} ***")
    w, h = utils.image_dimensions(path)
    new_w, new_h = fix_ratio(w + border, h + border, ratio)
    if new_w == w and new_h == h:
        logging.info("no resize needed")
        return
    logging.info(f"{w}x{h} -> {new_w}x{new_h} (border: {border})")
    resize(dry_run, new_h, new_w, path)


def resize(dry_run: bool, new_h: int, new_w: int, path: str) -> None:
    """
    Use ImageMagick to create a padded version. Overwrite the original file unless in dry-run mode.
    :param dry_run:
    :param new_h:
    :param new_w:
    :param path: image file
    :return:
    """
    cmd = ["convert", path, "-background", "#dddddd", "-gravity", "center", "-extent", f"{new_w}x{new_h}"]
    if dry_run:
        logging.info(f"[DRY RUN] Would pad and overwrite: {' '.join(cmd)}")
        return
    tmp = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
    tmp.close()  # Avoids issues on Windows
    tmp_path = tmp.name
    cmd.append(tmp_path)
    try:
        result = subprocess.run(cmd, stderr=subprocess.PIPE)
        if result.returncode != 0:
            raise RuntimeError(f"Error processing {path}: {result.stderr.decode().strip()}")
        # Replace original file
        shutil.move(tmp_path, path)
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
    logging.info(f"Updated: {path}")


def main() -> None:
    args = parse_args()
    if args.quiet:
        logging.getLogger().setLevel(logging.WARNING)
    for img in args.images:
        process_image(img, args.border, args.dry_run, args.ratio)


if __name__ == "__main__":
    main()
