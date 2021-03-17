# py-staticmaps
# Copyright (c) 2020 Florian Pigorsch; see /LICENSE for licensing information

import pytest  # type: ignore

import staticmaps


def test_parse_latlng() -> None:
    bad = [
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
    ]
    for s in bad:
        with pytest.raises(ValueError):
            staticmaps.parse_latlng(s)

    good = ["48,8", " 48 , 8 ", "-48,8", "+48,8", "48,-8", "48,+8", "48.123,8.456"]
    for s in good:
        c = staticmaps.parse_latlng(s)
        assert c.is_valid()


def test_parse_latlngs() -> None:
    good = [("", 0), ("48,8", 1), ("48,8 47,7", 2), ("   48,8    47,7   ", 2), ("48,7 48,8 47,7", 3)]
    for s, expected_len in good:
        a = staticmaps.parse_latlngs(s)
        assert len(a) == expected_len

    bad = ["xyz", "48,8 xyz", "48,8 48,181"]
    for s in bad:
        with pytest.raises(ValueError):
            staticmaps.parse_latlngs(s)


def test_parse_latlngs2rect() -> None:
    good = ["48,8 47,7", "   48,8    47,7   "]
    for s in good:
        r = staticmaps.parse_latlngs2rect(s)
        assert r.is_valid()

    bad = ["xyz", "48,8 xyz", "48,8 48,181", "48,7", "48,7 48,8 47,7"]
    for s in bad:
        with pytest.raises(ValueError):
            staticmaps.parse_latlngs2rect(s)
