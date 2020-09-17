import pytest
import staticmaps


def test_bad_creation() -> None:
    with pytest.raises(ValueError):
        staticmaps.Line([])

    with pytest.raises(ValueError):
        staticmaps.Line([staticmaps.create_latlng(48, 8)])

    with pytest.raises(ValueError):
        staticmaps.Line([staticmaps.create_latlng(48, 8), staticmaps.create_latlng(49, 9)], width=-123)


def test_creation() -> None:
    staticmaps.Line(
        [staticmaps.create_latlng(48, 8), staticmaps.create_latlng(49, 9), staticmaps.create_latlng(50, 8)],
        color=staticmaps.YELLOW,
    )


def test_bounds() -> None:
    line = staticmaps.Line(
        [staticmaps.create_latlng(48, 8), staticmaps.create_latlng(49, 9), staticmaps.create_latlng(50, 8)],
        color=staticmaps.YELLOW,
    )
    assert not line.bounds().is_point()
