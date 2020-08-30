import s2sphere  # type: ignore
import staticmaps


def test_creation() -> None:
    staticmaps.Marker(s2sphere.LatLng.from_degrees(48, 8), color=staticmaps.YELLOW, size=8)


def test_bounds() -> None:
    marker = staticmaps.Marker(s2sphere.LatLng.from_degrees(48, 8))
    assert marker.bounds().is_point()
