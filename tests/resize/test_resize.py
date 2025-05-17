import pytest
from unittest import mock
import subprocess
import tempfile
import shutil
import os
import logging
from typing import Tuple, List, Generator

from image_manipulation.resize import resize


@pytest.fixture
def mock_dependencies() -> Generator[Tuple[mock.MagicMock, mock.MagicMock, mock.MagicMock, mock.MagicMock], None, None]:
    """Fixture to mock the dependencies used in the resize function."""
    with (
        mock.patch("subprocess.run") as mock_run,
        mock.patch("tempfile.NamedTemporaryFile") as mock_tempfile,
        mock.patch("shutil.move") as mock_move,
        mock.patch("os.remove") as mock_remove,
    ):
        yield mock_run, mock_tempfile, mock_move, mock_remove


@pytest.fixture
def mock_file_exists() -> Generator[Tuple[mock.MagicMock], None, None]:
    with mock.patch("os.path.exists") as mock_exists:
        yield mock_exists


@pytest.mark.parametrize(
    "dry_run, expected_call, expected_log",
    [
        (True, 0, "[DRY RUN]"),  # Dry run, no actual subprocess call, check log
        (False, 1, "Updated"),  # No dry run, subprocess should be called, check log for update
    ],
)
def test_resize(
    dry_run: bool,
    expected_call: int,
    expected_log: str,
    mock_dependencies: Tuple[mock.MagicMock, mock.MagicMock, mock.MagicMock, mock.MagicMock],
) -> None:
    # Arrange
    new_h = 800
    new_w = 600
    path = "image.jpg"
    cmd = ["convert", path, "-background", "#dddddd", "-gravity", "center", "-extent", f"{new_w}x{new_h}", "tmp2.jpg"]

    mock_run, mock_tempfile, mock_move, mock_remove = mock_dependencies

    mock_tempfile.return_value.name = "tmp2.jpg"
    mock_run.return_value.returncode = 0  # Simulate successful run
    mock_move.return_value = None  # Simulate successful move

    # Act
    resize(dry_run, new_h, new_w, path)

    # Assert
    if dry_run:
        mock_run.assert_not_called()
        mock_move.assert_not_called()
        mock_remove.assert_not_called()
    else:
        mock_run.assert_called_once_with(cmd, stderr=subprocess.PIPE)
        mock_move.assert_called_once_with("tmp2.jpg", path)
        mock_remove.assert_not_called()


@pytest.mark.parametrize(
    "returncode, expected_exception",
    [
        (1, RuntimeError),  # Simulate subprocess error
        (0, None),  # No error
    ],
)
def test_resize_subprocess_error_handling(
    returncode: int,
    expected_exception: type[RuntimeError] | None,
    mock_dependencies: Tuple[mock.MagicMock, mock.MagicMock, mock.MagicMock, mock.MagicMock],
    mock_file_exists: mock.MagicMock,
) -> None:
    # Arrange
    dry_run = False
    new_h = 800
    new_w = 600
    path = "image.jpg"

    mock_run, mock_tempfile, mock_move, mock_remove = mock_dependencies
    mock_tempfile.return_value.name = "tmp2.jpg"
    mock_run.return_value.returncode = returncode  # Simulate subprocess error or success
    mock_run.return_value.stderr = b"Error occurred" if returncode != 0 else b""
    mock_file_exists.return_value = expected_exception

    # Act & Assert
    if expected_exception:
        with pytest.raises(expected_exception, match="Error processing image.jpg"):
            resize(dry_run, new_h, new_w, path)
        mock_move.assert_not_called()
        mock_remove.assert_called_once_with("tmp2.jpg")
    else:
        resize(dry_run, new_h, new_w, path)
        mock_move.assert_called_once_with("tmp2.jpg", "image.jpg")
        mock_remove.assert_not_called()

    mock_run.assert_called_once_with(
        ["convert", "image.jpg", "-background", "#dddddd", "-gravity", "center", "-extent", "600x800", "tmp2.jpg"],
        stderr=subprocess.PIPE,
    )
