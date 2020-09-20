# py-staticmaps
# Copyright (c) 2020 Florian Pigorsch; see /LICENSE for licensing information

import pytest  # type: ignore
import staticmaps


def test_parse_color() -> None:
    bad = [
        "",
        "aaa",
        "midnightblack",
        "#123",
        "#12345",
        "#1234567",
    ]
    for s in bad:
        with pytest.raises(ValueError):
            staticmaps.parse_color(s)

    good = ["0x1a2b3c", "0x1A2B3C", "#1a2b3c", "0x1A2B3C", "0x1A2B3C4D", "black", "RED", "Green", "transparent"]
    for s in good:
        staticmaps.parse_color(s)


def test_create() -> None:
    bad = [
        (-1, 0, 0),
        (256, 0, 0),
        (0, -1, 0),
        (0, 256, 0),
        (0, 0, -1),
        (0, 0, 256),
        (0, 0, 0, -1),
        (0, 0, 0, 256),
    ]
    for rgb in bad:
        with pytest.raises(ValueError):
            staticmaps.Color(*rgb)

    staticmaps.Color(1, 2, 3)
    staticmaps.Color(1, 2, 3, 4)
