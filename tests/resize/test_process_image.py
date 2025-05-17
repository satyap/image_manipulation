from typing import Tuple, Generator
from unittest import mock

import pytest

from image_manipulation.resize import process_image


@pytest.fixture
def mock_dependencies() -> Generator[Tuple[mock.MagicMock, mock.MagicMock, mock.MagicMock], None, None]:
    with (
        mock.patch("image_manipulation.utils.image_dimensions") as mock_image_dimensions,
        mock.patch("image_manipulation.resize.fix_ratio") as mock_fix_ratio,
        mock.patch("image_manipulation.resize.resize") as mock_resize,
    ):
        yield mock_image_dimensions, mock_fix_ratio, mock_resize


def test_process_image_no_resize(mock_dependencies: Tuple[mock.MagicMock, mock.MagicMock, mock.MagicMock]) -> None:
    mock_image_dimensions, mock_fix_ratio, mock_resize = mock_dependencies
    mock_image_dimensions.return_value = (800, 600)  # Mock current image dimensions
    mock_fix_ratio.return_value = (800, 600)  # No resizing needed (same dimensions)

    path = "image.jpg"
    border = 10
    dry_run = False
    ratio = "4x6"

    process_image(path, border, dry_run, ratio)

    mock_resize.assert_not_called()


def test_process_image_with_resize(mock_dependencies: Tuple[mock.MagicMock, mock.MagicMock, mock.MagicMock]) -> None:
    mock_image_dimensions, mock_fix_ratio, mock_resize = mock_dependencies
    mock_image_dimensions.return_value = (800, 600)
    mock_fix_ratio.return_value = (600, 800)

    path = "image.jpg"
    dry_run = False

    process_image(path, 10, dry_run, "4x6")

    mock_resize.assert_called_once_with(dry_run, 800, 600, path)
