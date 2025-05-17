import argparse
from typing import Optional, Tuple
from unittest.mock import call, MagicMock

import pytest
from pytest_mock import MockerFixture

from image_manipulation.annotate import ImageAnnotate


@pytest.fixture
def annotate() -> ImageAnnotate:
    args = argparse.Namespace(
        text_size=50,
        border=40,
        text="hello there",
        input_file="my_input",
        output_file="my_output",
        orientation="t-r-v",
        verbose=True,
    )
    return ImageAnnotate(args)


@pytest.fixture
def mock_subprocess(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("subprocess.run")


@pytest.fixture
def mock_image_dimension(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("image_manipulation.annotate.utils.image_dimensions")


def test_labelimg(annotate: ImageAnnotate, mock_subprocess: MagicMock) -> None:
    mock_subprocess.return_value.stdout = "my label"
    assert annotate.labelimg() == "my label"
    assert mock_subprocess.call_args_list == [
        call(
            [
                # fmt: off
                "convert", "-density", "100", "-pointsize", "50",
                "-background", "#00000099", "-fill", "white", "-gravity", "center", "-font", "Liberation-Serif",
                "label: hello there",
                "-strokewidth", "8", "-rotate", "90", "miff:-",
                # fmt: on
            ],
            capture_output=True,
            check=True,
        )
    ]


@pytest.mark.parametrize(
    "orientation,expected_geometry",
    [
        ("top-right-vertical", "+210+40"),
        ("t-r-horizontal", "+200+40"),
        ("t-left-v", "+40+40"),
        ("t-l-h", "+40+40"),
        ("t-middle-v", "+125+40"),
        ("t-m-h", "+120+40"),
        ("bottom-r-v", "+210+100"),
        ("b-r-h", "+200+110"),
        ("b-l-v", "+40+100"),
        ("b-l-h", "+40+110"),
        ("b-m-v", "+125+100"),
        ("b-m-h", "+120+110"),
        ("middle-r-v", "+210+70"),
        ("m-r-h", "+200+75"),
        ("m-l-v", "+40+70"),
        ("m-l-h", "+40+75"),
        ("m-m-v", "+125+70"),
        ("m-m-h", "+120+75"),
    ],
)
def test_composite_cmd(
    annotate: ImageAnnotate, mock_image_dimension: MagicMock, orientation: str, expected_geometry: str
) -> None:
    def dimension(file: str | None = None, _stdin: Optional[bytes] = None) -> Tuple[int, int]:
        if not file:
            # simulate label rotation, which happens when label is generated.
            if orientation.endswith("h") or orientation.endswith("horizontal"):
                return 60, 50
            else:
                return 50, 60
        elif file == "my_input":
            return 300, 200
        else:
            raise RuntimeError(f"wrong file param {repr(file)}")

    annotate.set_orientation(orientation)
    mock_image_dimension.side_effect = dimension
    assert annotate.composite_cmd("".encode()) == [
        # fmt: off
        "composite", "-compose", "atop", "-geometry", expected_geometry, "-",
        "my_input", "my_output",
        # fmt: on
    ]
