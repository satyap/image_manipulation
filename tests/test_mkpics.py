from unittest.mock import MagicMock

import piexif
import pytest
from pytest_mock import MockerFixture

from image_manipulation import mkpics


@pytest.fixture()
def get_new_filename(mocker: MockerFixture) -> MagicMock:
    mock = mocker.patch("image_manipulation.mkpics.new_filename")
    mock.return_value = ("20200405", "newname")
    return mock


@pytest.fixture()
def exif(mocker: MockerFixture) -> MagicMock:
    mock = mocker.patch("image_manipulation.mkpics.Image")
    img = mock.open.return_value
    return img


annotation_without_xml = """ima-annotate \\
    -t " 20200405 - " \\
    -i xyz.jpg -o newname
"""

annotation_with_xml = """ima-annotate \\
    -t " 20200405 - " \\
    -i xyz.jpg -o newname
cat <<EOT > newname.xml
<?xml version="1.0" encoding="UTF-8"?><image><description>
      <field name="description"> </field>
      <field name="title"> </field>
      <field name="date"> 20200405 </field>
   </description> <bins> </bins> <exif> </exif> </image>
EOT
"""


@pytest.mark.parametrize(
    "file,prefix,xml,expected",
    [
        ("xyz.jpg", "k", False, annotation_without_xml),
        ("xyz.jpg", "k", True, annotation_with_xml),
    ],
)
def test_get_annotation(file: str, prefix: str, xml: bool, expected: str, get_new_filename: MagicMock) -> None:
    assert mkpics.annotation(file, prefix, xml) == expected


exif_with_original_date = {"Exif": {piexif.ExifIFD.DateTimeOriginal: "2020:03:04 19:39:12"}}
exif_with_modified_date = {"0th": {piexif.ImageIFD.DateTime: "2020:03:05 19:39:12"}}


@pytest.mark.parametrize(
    "file,prefix,exif_to_return,expected",
    [
        ("xyz.jpg", "k", exif_with_original_date, ("20200304", "k03041939.jpg")),
        ("xyz.jpg", "k", exif_with_modified_date, ("20200305", "k03051939.jpg")),
        ("IMG-20200712-WA01234.jpg", "k", None, ("20200712", "k07120123.jpg")),
    ],
)
def test_get_new_filename(
    file: str,
    prefix: str,
    exif_to_return: str,
    expected: tuple[str, str],
    exif: MagicMock,
) -> None:
    exif.info = {}
    if exif_to_return:
        exif.info = {"exif": piexif.dump(exif_to_return)}
    assert mkpics.new_filename(file, prefix) == expected
