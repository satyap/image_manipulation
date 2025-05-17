from unittest.mock import patch, Mock

import pytest

from image_manipulation.utils import image_dimensions


@pytest.mark.parametrize(
    "file_arg,stdin_arg,expected_output,expected_call",
    [
        ("image.jpg", None, [640, 480], ["identify", "-format", "%w %h", "image.jpg"]),
        ("-", b"fake-bytes", [1024, 768], ["identify", "-format", "%w %h", "-"]),
    ],
)
def test_image_dimensions_success(
    file_arg: str, stdin_arg: bytes | None, expected_output: tuple[int, int], expected_call: list[str]
) -> None:
    mock_result = Mock()
    mock_result.returncode = 0
    mock_result.stdout = f"{expected_output[0]} {expected_output[1]}"
    mock_result.stderr = b""

    with patch("subprocess.run", return_value=mock_result) as mock_run:
        dims = list(image_dimensions(file=file_arg, stdin=stdin_arg))
        assert dims == expected_output
        mock_run.assert_called_once_with(expected_call, input=stdin_arg, capture_output=True, check=True)


def test_image_dimensions_error() -> None:
    mock_result = Mock()
    mock_result.returncode = 1
    mock_result.stdout = b""
    mock_result.stderr = b"identify: unable to read image"

    with patch("subprocess.run", return_value=mock_result):
        with pytest.raises(RuntimeError, match="Error reading image dimensions"):
            list(image_dimensions("bad.jpg"))
