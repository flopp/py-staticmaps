import pytest  # type: ignore
import s2sphere as s2  # type: ignore
import staticmaps
from .mock_tile_downloader import MockTileDownloader


def test_bounds() -> None:
    context = staticmaps.Context()
    assert context.object_bounds() is None

    context.add_object(staticmaps.Marker(s2.LatLng.from_degrees(48, 8)))
    bounds = context.object_bounds()
    assert bounds is not None
    assert bounds.is_point()

    context.add_object(staticmaps.Marker(s2.LatLng.from_degrees(47, 7)))
    assert context.object_bounds() is not None
    assert context.object_bounds() == s2.LatLngRect(s2.LatLng.from_degrees(47, 7), s2.LatLng.from_degrees(48, 8))

    context.add_object(staticmaps.Marker(s2.LatLng.from_degrees(47.5, 7.5)))
    assert context.object_bounds() is not None
    assert context.object_bounds() == s2.LatLngRect(s2.LatLng.from_degrees(47, 7), s2.LatLng.from_degrees(48, 8))


def test_render_empty() -> None:
    context = staticmaps.Context()
    with pytest.raises(RuntimeError):
        context.render(200, 100)


def test_render_center_zoom() -> None:
    context = staticmaps.Context()
    context.set_tile_downloader(MockTileDownloader())
    context.set_center(s2.LatLng.from_degrees(48, 8))
    context.set_zoom(15)
    image = context.render(200, 100)
    assert image.get_width() == 200
    assert image.get_height() == 100
