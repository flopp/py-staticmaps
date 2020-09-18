# py-staticmaps
# Copyright (c) 2020 Florian Pigorsch; see /LICENSE for licensing information

import random
import re
import typing


class Color:
    def __init__(self, r: int, g: int, b: int):
        if not 0x00 <= r <= 0xFF:
            raise ValueError(f"'r' component out of range (must be 0-255): {r}")
        if not 0x00 <= g <= 0xFF:
            raise ValueError(f"'g' component out of range (must be 0-255): {g}")
        if not 0x00 <= b <= 0xFF:
            raise ValueError(f"'b' component out of range (must be 0-255): {b}")
        self._r = r
        self._g = g
        self._b = b

    def text_color(self) -> "Color":
        luminance = 0.299 * self._r + 0.587 * self._g + 0.114 * self._b
        return BLACK if luminance >= 0x7F else WHITE

    def hex_string(self) -> str:
        return f"#{self._r:02x}{self._g:02x}{self._b:02x}"

    def float_rgb(self) -> typing.Tuple[float, float, float]:
        return self._r / 255.0, self._g / 255.0, self._b / 255.0


BLACK = Color(0x00, 0x00, 0x00)
WHITE = Color(0xFF, 0xFF, 0xFF)
BLUE = Color(0x00, 0x00, 0xFF)
BROWN = Color(0x96, 0x4B, 0x00)
GREEN = Color(0x00, 0xFF, 0x00)
ORANGE = Color(0xFF, 0x7F, 0x00)
PURPLE = Color(0x7F, 0x00, 0x7F)
RED = Color(0xFF, 0x00, 0x00)
YELLOW = Color(0xFF, 0xFF, 0x00)


def parse_color(s: str) -> Color:
    re_rgb = re.compile(r"^(0x|#)([a-f0-9]){6}$")

    s = s.strip().lower()

    m = re_rgb.match(s)
    if m:
        v = int("0x" + m[2], 16)
        return Color(
            ((v << 16) & 0xFF),
            ((v << 8) & 0xFF),
            (v & 0xFF),
        )

    color_map = {
        "black": BLACK,
        "blue": BLUE,
        "brown": BROWN,
        "green": GREEN,
        "orange": ORANGE,
        "purple": PURPLE,
        "red": RED,
        "yellow": YELLOW,
        "white": WHITE,
    }
    if s in color_map:
        return color_map[s]

    raise ValueError(f"Cannot parse color string: {s}")


def random_color() -> Color:
    return random.choice(
        [
            BLACK,
            BLUE,
            BROWN,
            GREEN,
            ORANGE,
            PURPLE,
            RED,
            YELLOW,
            WHITE,
        ]
    )
