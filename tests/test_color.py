"""py-staticmaps - Test Color"""
# Copyright (c) 2020 Florian Pigorsch; see /LICENSE for licensing information

import math
import pytest  # type: ignore
import staticmaps


def test_text_color() -> None:
    white = [
        (0, 0, 0),
        (255, 0, 0),
        (0, 0, 255),
        (0, 0, 0, 0),
        (0, 0, 0, 255),
    ]
    for rgb in white:
        color = staticmaps.Color(*rgb)
        assert staticmaps.WHITE == color.text_color()
        assert staticmaps.WHITE.int_rgb() == color.text_color().int_rgb()

    black = [
        (0, 255, 0),
        (255, 255, 0),
        (0, 255, 255),
        (255, 255, 255),
    ]
    for rgb in black:
        color = staticmaps.Color(*rgb)
        assert staticmaps.BLACK == color.text_color()
        assert staticmaps.BLACK.int_rgb() == color.text_color().int_rgb()


def test_hex_rgb() -> None:
    colors = [
        ((0, 0, 0), "#000000"),
        ((255, 0, 0), "#ff0000"),
        ((0, 255, 0), "#00ff00"),
        ((0, 0, 255), "#0000ff"),
        ((255, 255, 0), "#ffff00"),
        ((0, 255, 255), "#00ffff"),
        ((255, 255, 255), "#ffffff"),
    ]
    for rgb, hex_color in colors:
        color = staticmaps.Color(*rgb)
        assert hex_color == color.hex_rgb()


def test_int_rgb() -> None:
    colors = [
        (0, 0, 0),
        (255, 0, 0),
        (0, 0, 255),
        (0, 255, 0),
        (255, 255, 0),
        (0, 255, 255),
        (255, 255, 255),
    ]
    for rgb in colors:
        color = staticmaps.Color(*rgb)
        assert rgb == color.int_rgb()


def test_int_rgba() -> None:
    colors = [
        (0, 0, 0, 0),
        (255, 0, 0, 0),
        (0, 0, 255, 255),
        (0, 255, 0, 255),
        (255, 255, 0, 0),
        (0, 255, 255, 0),
        (255, 255, 255, 255),
    ]
    for rgb in colors:
        color = staticmaps.Color(*rgb)
        assert rgb == color.int_rgba()


def test_float_rgb() -> None:
    colors = [
        ((0, 0, 0), (0.0, 0.0, 0.0)),
        ((255, 0, 0), (1.0, 0.0, 0.0)),
        ((0, 255, 0), (0.0, 1.0, 0.0)),
        ((0, 0, 255), (0.0, 0.0, 1.0)),
        ((255, 255, 0), (1.0, 1.0, 0.0)),
        ((0, 255, 255), (0.0, 1.0, 1.0)),
        ((255, 255, 255), (1.0, 1.0, 1.0)),
    ]
    for rgb, float_color in colors:
        color = staticmaps.Color(*rgb)
        assert float_color == color.float_rgb()


def test_float_rgba() -> None:
    colors = [
        ((0, 0, 0), (0.0, 0.0, 0.0, 1.0)),
        ((0, 0, 0, 0), (0.0, 0.0, 0.0, 0.0)),
        ((255, 0, 0, 0), (1.0, 0.0, 0.0, 0.0)),
        ((0, 255, 0, 255), (0.0, 1.0, 0.0, 1.0)),
        ((0, 0, 255, 255), (0.0, 0.0, 1.0, 1.0)),
        ((255, 255, 0, 0), (1.0, 1.0, 0.0, 0.0)),
        ((0, 255, 255, 0), (0.0, 1.0, 1.0, 0.0)),
        ((255, 255, 255, 255), (1.0, 1.0, 1.0, 1.0)),
        ((0, 0, 0), (0.0, 0.0, 0.0, 1.0)),
        ((255, 255, 255), (1.0, 1.0, 1.0, 1.0)),
    ]
    for rgb, float_color in colors:
        color = staticmaps.Color(*rgb)
        assert float_color == color.float_rgba()


def test_float_a() -> None:
    colors = [
        ((0, 0, 0, 0), 0.0),
        ((255, 255, 255, 255), 1.0),
        ((0, 0, 0), 1.0),
        ((255, 255, 255), 1.0),
        ((255, 255, 255, 100), 0.39215663),
        ((255, 255, 255, 200), 0.78431373),
    ]
    for rgb, float_alpha in colors:
        color = staticmaps.Color(*rgb)
        assert math.isclose(float_alpha, color.float_a(), rel_tol=0.0001)


def test_parse_color() -> None:
    good = ["0x1a2b3c", "0x1A2B3C", "#1a2b3c", "0x1A2B3C", "0x1A2B3C4D", "black", "RED", "Green", "transparent"]
    for s in good:
        staticmaps.parse_color(s)


def test_parse_color_raises_value_error() -> None:
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


def test_create() -> None:
    staticmaps.Color(1, 2, 3)
    staticmaps.Color(1, 2, 3, 4)


def test_create_raises_value_error() -> None:
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


def test_random_color() -> None:
    colors = [
        staticmaps.BLACK,
        staticmaps.BLUE,
        staticmaps.BROWN,
        staticmaps.GREEN,
        staticmaps.ORANGE,
        staticmaps.PURPLE,
        staticmaps.RED,
        staticmaps.YELLOW,
        staticmaps.WHITE,
    ]
    for _ in [0, 10]:
        assert staticmaps.random_color() in colors
