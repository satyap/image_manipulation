import subprocess
from typing import Optional, Dict, Tuple


def image_dimensions(file: str | None = None, stdin: Optional[bytes] = None) -> tuple[int, int]:
    """
    Return horizontal or vertical size of given image file, or of the binary blob.
    Binary blob is a bytes object as used by `subprocess`.
    :param dim: 'h' or 'w' for height or width.
    :param file: File name, or '-' in order to use the binary blob in `stdin`.
    :param stdin: Optional text blob whose size is wanted.
    :return: The required dimension size in pixels.
    """
    if not file:
        file = "-"
    result = subprocess.run(["identify", "-format", "%w %h", file], input=stdin, capture_output=True, check=True)

    if result.returncode != 0:
        raise RuntimeError(f"Error reading image dimensions for {file}: {result.stderr.decode().strip()}")

    parts = result.stdout.strip().split()
    if len(parts) != 2:
        raise ValueError(f"Unexpected output from `identify`: {result.stdout!r}")
    try:
        width, height = map(int, parts)
    except ValueError as e:
        raise ValueError(f"Non-integer output from `identify`: {parts!r}") from e

    return width, height
