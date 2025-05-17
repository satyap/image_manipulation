from typing import Tuple

import pytest

from image_manipulation.resize import fix_ratio


@pytest.mark.parametrize(
    "w,h,ratio_key,expected",
    [
        (600, 900, "4x6", (600, 900)),  # portrait, already 4x6
        (900, 600, "4x6", (900, 600)),  # landscape, already 6x4
        (800, 600, "4x6", (900, 600)),  # not wide enough (too tall)
        (600, 1200, "4x6", (800, 1200)),  # not tall enough (too wide)
        (700, 700, "5x7", (700, 980)),  # square input to 5:7
        (1400, 1000, "8x10", (1400, 1120)),  # not tall enough
        (1000, 1400, "8x10", (1120, 1400)),  # not wide enough
    ],
)
def test_fix_ratio(w: int, h: int, ratio_key: str, expected: Tuple[int, int]) -> None:
    assert fix_ratio(w, h, ratio_key) == expected
