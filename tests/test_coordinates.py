"""py-staticmaps - Test Coordinates"""
# Copyright (c) 2020 Florian Pigorsch; see /LICENSE for licensing information

import pytest  # type: ignore

import staticmaps


@pytest.mark.parametrize("good", ["48,8", " 48 , 8 ", "-48,8", "+48,8", "48,-8", "48,+8", "48.123,8.456"])
def test_parse_latlng(good: str) -> None:
    c = staticmaps.parse_latlng(good)
    assert c.is_valid()


@pytest.mark.parametrize(
    "bad",
    [
        "",
        "aaa",
        "12",
        "1,2,3",
        "48,",
        "48,x",
        "4 8,8",
        "91,8",
        "-91,8",
        "48,-181",
        "48,181",
    ],
)
def test_parse_latlng_raises_value_error(bad: str) -> None:
    with pytest.raises(ValueError):
        staticmaps.parse_latlng(bad)


@pytest.mark.parametrize(
    "good, expected_len", [("", 0), ("48,8", 1), ("48,8 47,7", 2), ("   48,8    47,7   ", 2), ("48,7 48,8 47,7", 3)]
)
def test_parse_latlngs(good: str, expected_len: int) -> None:
    a = staticmaps.parse_latlngs(good)
    assert len(a) == expected_len


@pytest.mark.parametrize("bad", ["xyz", "48,8 xyz", "48,8 48,181"])
def test_parse_latlngs_raises_value_error(bad: str) -> None:
    with pytest.raises(ValueError):
        staticmaps.parse_latlngs(bad)


@pytest.mark.parametrize("good", ["48,8 47,7", "   48,8    47,7   "])
def test_parse_latlngs2rect(good: str) -> None:
    r = staticmaps.parse_latlngs2rect(good)
    assert r.is_valid()


@pytest.mark.parametrize("bad", ["xyz", "48,8 xyz", "48,8 48,181", "48,7", "48,7 48,8 47,7"])
def test_parse_latlngs2rect_raises_value_error(bad: str) -> None:
    with pytest.raises(ValueError):
        staticmaps.parse_latlngs2rect(bad)
