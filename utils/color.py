from typing import List
from ..base.pyg_types import Color, Number


def combine(a: Color, b: Color, amt: Number) -> Color:
    return int(b[0] * amt + a[0] * (1 - amt)), int(b[1] * amt + a[1] * (1 - amt)), int(b[2] * amt + a[2] * (1 - amt))


def init_gradient(lst: List[Color], start: Color, end: Color):
    for c in range(len(lst)):
        lst[c] = combine(start, end, float(c) / len(lst))


def mul_color(a: Color, amt: Number) -> Color:
    return int(a[0] * amt), int(a[1] * amt), int(a[2] * amt)
