"""py-staticmaps - Test Color"""
# Copyright (c) 2020 Florian Pigorsch; see /LICENSE for licensing information

import math

import pytest  # type: ignore

import staticmaps


@pytest.mark.parametrize(
    "rgb",
    [
        (0, 0, 0),
        (255, 0, 0),
        (0, 0, 255),
        (0, 0, 0, 0),
        (0, 0, 0, 255),
    ],
)
def test_text_color_white(rgb: tuple) -> None:
    color = staticmaps.Color(*rgb)
    assert staticmaps.WHITE == color.text_color()
    assert staticmaps.WHITE.int_rgb() == color.text_color().int_rgb()


@pytest.mark.parametrize(
    "rgb",
    [
        (0, 255, 0),
        (255, 255, 0),
        (0, 255, 255),
        (255, 255, 255),
    ],
)
def test_text_color_black(rgb: tuple) -> None:
    color = staticmaps.Color(*rgb)
    assert staticmaps.BLACK == color.text_color()
    assert staticmaps.BLACK.int_rgb() == color.text_color().int_rgb()


@pytest.mark.parametrize(
    "rgb, hex_color",
    [
        ((0, 0, 0), "#000000"),
        ((255, 0, 0), "#ff0000"),
        ((0, 255, 0), "#00ff00"),
        ((0, 0, 255), "#0000ff"),
        ((255, 255, 0), "#ffff00"),
        ((0, 255, 255), "#00ffff"),
        ((255, 255, 255), "#ffffff"),
    ],
)
def test_hex_rgb(rgb: tuple, hex_color: str) -> None:
    color = staticmaps.Color(*rgb)
    assert hex_color == color.hex_rgb()


@pytest.mark.parametrize(
    "rgb",
    [
        (0, 0, 0),
        (255, 0, 0),
        (0, 0, 255),
        (0, 255, 0),
        (255, 255, 0),
        (0, 255, 255),
        (255, 255, 255),
    ],
)
def test_int_rgb(rgb: tuple) -> None:
    color = staticmaps.Color(*rgb)
    assert rgb == color.int_rgb()


@pytest.mark.parametrize(
    "rgb",
    [
        (0, 0, 0, 0),
        (255, 0, 0, 0),
        (0, 0, 255, 255),
        (0, 255, 0, 255),
        (255, 255, 0, 0),
        (0, 255, 255, 0),
        (255, 255, 255, 255),
    ],
)
def test_int_rgba(rgb: tuple) -> None:
    color = staticmaps.Color(*rgb)
    assert rgb == color.int_rgba()


@pytest.mark.parametrize(
    "rgb, float_color",
    [
        ((0, 0, 0), (0.0, 0.0, 0.0)),
        ((255, 0, 0), (1.0, 0.0, 0.0)),
        ((0, 255, 0), (0.0, 1.0, 0.0)),
        ((0, 0, 255), (0.0, 0.0, 1.0)),
        ((255, 255, 0), (1.0, 1.0, 0.0)),
        ((0, 255, 255), (0.0, 1.0, 1.0)),
        ((255, 255, 255), (1.0, 1.0, 1.0)),
    ],
)
def test_float_rgb(rgb: tuple, float_color: tuple) -> None:
    color = staticmaps.Color(*rgb)
    assert float_color == color.float_rgb()


@pytest.mark.parametrize(
    "rgb, float_color",
    [
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
    ],
)
def test_float_rgba(rgb: tuple, float_color: tuple) -> None:
    color = staticmaps.Color(*rgb)
    assert float_color == color.float_rgba()


@pytest.mark.parametrize(
    "rgb, float_alpha",
    [
        ((0, 0, 0, 0), 0.0),
        ((255, 255, 255, 255), 1.0),
        ((0, 0, 0), 1.0),
        ((255, 255, 255), 1.0),
        ((255, 255, 255, 100), 0.39215663),
        ((255, 255, 255, 200), 0.78431373),
    ],
)
def test_float_a(rgb: tuple, float_alpha: float) -> None:
    color = staticmaps.Color(*rgb)
    assert math.isclose(float_alpha, color.float_a(), rel_tol=0.0001)


@pytest.mark.parametrize(
    "good", ["0x1a2b3c", "0x1A2B3C", "#1a2b3c", "0x1A2B3C", "0x1A2B3C4D", "black", "RED", "Green", "transparent"]
)
def test_parse_color(good: str) -> None:
    staticmaps.parse_color(good)


@pytest.mark.parametrize(
    "bad",
    [
        "",
        "aaa",
        "midnightblack",
        "#123",
        "#12345",
        "#1234567",
    ],
)
def test_parse_color_raises_value_error(bad: str) -> None:
    with pytest.raises(ValueError):
        staticmaps.parse_color(bad)


def test_create() -> None:
    staticmaps.Color(1, 2, 3)
    staticmaps.Color(1, 2, 3, 4)


@pytest.mark.parametrize(
    "rgb",
    [
        (-1, 0, 0),
        (256, 0, 0),
        (0, -1, 0),
        (0, 256, 0),
        (0, 0, -1),
        (0, 0, 256),
        (0, 0, 0, -1),
        (0, 0, 0, 256),
    ],
)
def test_create_raises_value_error(rgb: tuple) -> None:
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
