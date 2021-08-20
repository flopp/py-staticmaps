# py-staticmaps
# Copyright (c) 2020 Florian Pigorsch; see /LICENSE for licensing information

import pytest  # type: ignore
import s2sphere  # type: ignore

import staticmaps

from .mock_tile_downloader import MockTileDownloader


def test_bounds() -> None:
    context = staticmaps.Context()
    assert context.object_bounds() is None

    context.add_object(staticmaps.Marker(staticmaps.create_latlng(48, 8)))
    bounds = context.object_bounds()
    assert bounds is not None
    assert bounds.is_point()

    context.add_object(staticmaps.Marker(staticmaps.create_latlng(47, 7)))
    assert context.object_bounds() is not None
    assert context.object_bounds() == s2sphere.LatLngRect(
        staticmaps.create_latlng(47, 7), staticmaps.create_latlng(48, 8)
    )

    context.add_object(staticmaps.Marker(staticmaps.create_latlng(47.5, 7.5)))
    assert context.object_bounds() is not None
    assert context.object_bounds() == s2sphere.LatLngRect(
        staticmaps.create_latlng(47, 7), staticmaps.create_latlng(48, 8)
    )

    context.add_bounds(s2sphere.LatLngRect(staticmaps.create_latlng(46, 6), staticmaps.create_latlng(49, 9)))
    assert context.object_bounds() is not None
    assert context.object_bounds() == s2sphere.LatLngRect(
        staticmaps.create_latlng(46, 6), staticmaps.create_latlng(49, 9)
    )

    context.add_bounds(s2sphere.LatLngRect(staticmaps.create_latlng(47.5, 7.5), staticmaps.create_latlng(48, 8)))
    assert context.object_bounds() is not None
    assert context.object_bounds() == s2sphere.LatLngRect(
        staticmaps.create_latlng(47, 7), staticmaps.create_latlng(48, 8)
    )


def test_render_empty() -> None:
    context = staticmaps.Context()
    with pytest.raises(RuntimeError):
        context.render_svg(200, 100)


def test_render_center_zoom() -> None:
    context = staticmaps.Context()
    context.set_tile_downloader(MockTileDownloader())
    context.set_center(staticmaps.create_latlng(48, 8))
    context.set_zoom(15)
    context.render_svg(200, 100)


def test_render_tight_on_markers():
    context = staticmaps.Context()

    # make bottom left and top right bounding box for map, happens to be Oxford and Norwich
    bottom_left = staticmaps.create_latlng(51.75, -1.25)
    top_right = staticmaps.create_latlng(52.63, 1.29)

    # make clean map
    _ = context.make_clean_map_from_bounding_box(bottom_left=bottom_left, top_right=top_right, width=1000, height=1000)
