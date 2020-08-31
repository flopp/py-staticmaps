import pytest
import s2sphere  # type: ignore
import staticmaps


def test_bad_creation() -> None:
    with pytest.raises(ValueError):
        staticmaps.Line([])

    with pytest.raises(ValueError):
        staticmaps.Line([s2sphere.LatLng.from_degrees(48, 8)])

    with pytest.raises(ValueError):
        staticmaps.Line([s2sphere.LatLng.from_degrees(48, 8), s2sphere.LatLng.from_degrees(49, 9)], width=-123)


def test_creation() -> None:
    staticmaps.Line(
        [s2sphere.LatLng.from_degrees(48, 8), s2sphere.LatLng.from_degrees(49, 9), s2sphere.LatLng.from_degrees(50, 8)],
        color=staticmaps.YELLOW,
    )


def test_bounds() -> None:
    line = staticmaps.Line(
        [s2sphere.LatLng.from_degrees(48, 8), s2sphere.LatLng.from_degrees(49, 9), s2sphere.LatLng.from_degrees(50, 8)],
        color=staticmaps.YELLOW,
    )
    assert not line.bounds().is_point()
