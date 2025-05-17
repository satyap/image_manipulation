import pytest
import sys
from unittest.mock import patch

from image_manipulation.resize import parse_args


def test_parse_args_default() -> None:
    with patch.object(sys, "argv", ["your_script_name.py", "x"]):
        args = parse_args()

    assert args.border == 0
    assert not args.dry_run
    assert not args.quiet
    assert args.ratio == "4x6"
    assert args.images == ["x"]  # No image file arguments


def test_parse_args_with_border() -> None:
    with patch.object(sys, "argv", ["your_script_name.py", "-b", "5", "image1.jpg"]):
        args = parse_args()

    assert args.border == 5
    assert args.images == ["image1.jpg"]


def test_parse_args_with_dry_run() -> None:
    with patch.object(sys, "argv", ["your_script_name.py", "-d", "image1.jpg"]):
        args = parse_args()

    assert args.dry_run
    assert args.images == ["image1.jpg"]


def test_parse_args_with_quiet() -> None:
    with patch.object(sys, "argv", ["your_script_name.py", "-q", "image1.jpg"]):
        args = parse_args()

    assert args.quiet
    assert args.images == ["image1.jpg"]


def test_parse_args_with_ratio() -> None:
    with patch.object(sys, "argv", ["your_script_name.py", "-r", "8x10", "image1.jpg"]):
        args = parse_args()

    assert args.ratio == "8x10"
    assert args.images == ["image1.jpg"]


def test_parse_args_multiple_images() -> None:
    with patch.object(sys, "argv", ["your_script_name.py", "image1.jpg", "image2.png"]):
        args = parse_args()

    assert args.images == ["image1.jpg", "image2.png"]


def test_parse_args_invalid_ratio() -> None:
    with patch.object(sys, "argv", ["your_script_name.py", "-r", "6x9", "image1.jpg"]):
        with pytest.raises(SystemExit):
            parse_args()
