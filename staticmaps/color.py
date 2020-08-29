import re
import typing

ColorT = typing.Tuple[float, float, float, float]


def parse_color(s: str) -> ColorT:
    re_rgba = re.compile(r"^(0x|#)([a-f0-9]){8}$")
    re_rgb = re.compile(r"^(0x|#)([a-f0-9]){6}$")

    s = s.strip().lower()

    m = re_rgba.match(s)
    if m:
        v = int("0x" + m[2], 16)
        return (
            ((v << 24) & 0xFF) / 0xFF,
            ((v << 16) & 0xFF) / 0xFF,
            ((v << 8) & 0xFF) / 0xFF,
            (v & 0xFF) / 0xFF,
        )

    m = re_rgb.match(s)
    if m:
        v = int("0x" + m[2], 16)
        return (
            ((v << 16) & 0xFF) / 0xFF,
            ((v << 8) & 0xFF) / 0xFF,
            (v & 0xFF) / 0xFF,
            1.0,
        )

    color_map = {
        "none": (0.0, 0.0, 0.0, 0.0),
        "transparent": (0.0, 0.0, 0.0, 0.0),
        "black": (0.0, 0.0, 0.0, 1.0),
        "blue": (0.0, 0.0, 1.0, 1.0),
        "brown": (0x96 / 0xFF, 0x4B / 0xFF, 0.0, 1.0),
        "green": (0.0, 1.0, 0.0, 1.0),
        "orange": (1.0, 0.5, 0.0, 1.0),
        "purple": (0.5, 0.0, 0.5, 1.0),
        "red": (1.0, 0.0, 0.0, 1.0),
        "yellow": (1.0, 1.0, 0.0, 1.0),
        "white": (1.0, 1.0, 1.0, 1.0),
    }
    if s in color_map:
        return color_map[s]

    raise ValueError("Cannot parse color string: {}".format(s))
