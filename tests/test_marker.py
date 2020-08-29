import pytest  # type: ignore
import s2sphere as s2  # type: ignore
import staticmaps


def test_creation_without_coordinates() -> None:
    with pytest.raises(ValueError):
        staticmaps.Marker(None)


def test_creation() -> None:
    staticmaps.Marker(s2.LatLng.from_degrees(48, 8))


def test_bounds() -> None:
    marker = staticmaps.Marker(s2.LatLng.from_degrees(48, 8))
    assert marker.bounds().is_point()
