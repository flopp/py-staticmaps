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
