#!/usr/bin/env python
"""py-staticmaps - Test Context"""

# py-staticmaps
# Copyright (c) 2020 Florian Pigorsch; see /LICENSE for licensing information

import pytest  # type: ignore
import s2sphere  # type: ignore

import staticmaps

from .mock_tile_downloader import MockTileDownloader


def test_add_marker_adds_bounds_is_point() -> None:
    context = staticmaps.Context()
    assert context.object_bounds() is None

    context.add_object(staticmaps.Marker(staticmaps.create_latlng(48, 8)))
    assert context.object_bounds() is not None
    assert context.object_bounds() == s2sphere.LatLngRect(
        staticmaps.create_latlng(48, 8), staticmaps.create_latlng(48, 8)
    )
    bounds = context.object_bounds()
    assert bounds is not None
    assert bounds.is_point()


def test_add_two_markers_adds_bounds_is_not_point() -> None:
    context = staticmaps.Context()
    assert context.object_bounds() is None

    context.add_object(staticmaps.Marker(staticmaps.create_latlng(47, 7)))
    assert context.object_bounds() is not None
    assert context.object_bounds() == s2sphere.LatLngRect(
        staticmaps.create_latlng(47, 7), staticmaps.create_latlng(47, 7)
    )
    context.add_object(staticmaps.Marker(staticmaps.create_latlng(48, 8)))
    assert context.object_bounds() == s2sphere.LatLngRect(
        staticmaps.create_latlng(47, 7), staticmaps.create_latlng(48, 8)
    )
    bounds = context.object_bounds()
    assert bounds is not None
    assert not bounds.is_point()


def test_add_line_adds_bounds_is_rect() -> None:
    context = staticmaps.Context()
    assert context.object_bounds() is None

    context.add_object(staticmaps.Line([staticmaps.create_latlng(47, 7), staticmaps.create_latlng(48, 8)]))
    assert context.object_bounds() is not None
    assert context.object_bounds() == s2sphere.LatLngRect(
        staticmaps.create_latlng(47, 7), staticmaps.create_latlng(48, 8)
    )


def test_add_greater_line_extends_bounds() -> None:
    context = staticmaps.Context()
    assert context.object_bounds() is None

    context.add_object(staticmaps.Line([staticmaps.create_latlng(47, 7), staticmaps.create_latlng(48, 8)]))
    assert context.object_bounds() is not None
    assert context.object_bounds() == s2sphere.LatLngRect(
        staticmaps.create_latlng(47, 7), staticmaps.create_latlng(48, 8)
    )
    context.add_object(staticmaps.Line([staticmaps.create_latlng(46, 6), staticmaps.create_latlng(49, 9)]))
    assert context.object_bounds() is not None
    assert context.object_bounds() == s2sphere.LatLngRect(
        staticmaps.create_latlng(46, 6), staticmaps.create_latlng(49, 9)
    )


def test_add_smaller_line_keeps_bounds() -> None:
    context = staticmaps.Context()
    assert context.object_bounds() is None

    context.add_object(staticmaps.Line([staticmaps.create_latlng(47, 7), staticmaps.create_latlng(48, 8)]))
    assert context.object_bounds() is not None
    assert context.object_bounds() == s2sphere.LatLngRect(
        staticmaps.create_latlng(47, 7), staticmaps.create_latlng(48, 8)
    )
    context.add_object(staticmaps.Line([staticmaps.create_latlng(47.5, 7.5), staticmaps.create_latlng(48, 8)]))
    assert context.object_bounds() is not None
    assert context.object_bounds() == s2sphere.LatLngRect(
        staticmaps.create_latlng(47, 7), staticmaps.create_latlng(48, 8)
    )


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


def test_add_greater_custom_bound_extends_bounds() -> None:
    context = staticmaps.Context()
    assert context.object_bounds() is None

    context.add_object(staticmaps.Marker(staticmaps.create_latlng(47, 7)))
    context.add_object(staticmaps.Marker(staticmaps.create_latlng(48, 8)))
    assert context.object_bounds() is not None

    context.add_bounds(s2sphere.LatLngRect(staticmaps.create_latlng(49, 7.5), staticmaps.create_latlng(49, 8)))
    assert context.object_bounds() == s2sphere.LatLngRect(
        staticmaps.create_latlng(47, 7), staticmaps.create_latlng(49, 8)
    )


def test_add_smaller_custom_bound_keeps_bounds() -> None:
    context = staticmaps.Context()
    assert context.object_bounds() is None

    context.add_object(staticmaps.Marker(staticmaps.create_latlng(47, 7)))
    context.add_object(staticmaps.Marker(staticmaps.create_latlng(48, 8)))
    assert context.object_bounds() is not None

    context.add_bounds(s2sphere.LatLngRect(staticmaps.create_latlng(47.5, 7.5), staticmaps.create_latlng(48, 8)))
    assert context.object_bounds() is not None
    assert context.object_bounds() == s2sphere.LatLngRect(
        staticmaps.create_latlng(47, 7), staticmaps.create_latlng(48, 8)
    )


def test_set_wrong_zoom_raises_exception() -> None:
    context = staticmaps.Context()
    with pytest.raises(ValueError):
        context.set_zoom(-1)
    with pytest.raises(ValueError):
        context.set_zoom(31)


def test_render_empty_raises_exception() -> None:
    context = staticmaps.Context()
    with pytest.raises(RuntimeError):
        context.render_svg(200, 100)


def test_render_center_zoom() -> None:
    context = staticmaps.Context()
    context.set_tile_downloader(MockTileDownloader())
    context.set_center(staticmaps.create_latlng(48, 8))
    context.set_zoom(15)
    context.render_svg(200, 100)


def test_render_with_zoom_without_center_raises_exception() -> None:
    context = staticmaps.Context()
    context.set_tile_downloader(MockTileDownloader())
    context.set_zoom(15)
    with pytest.raises(RuntimeError):
        context.render_svg(200, 100)


def test_render_with_center_without_zoom_sets_zoom_15() -> None:
    context = staticmaps.Context()
    context.set_tile_downloader(MockTileDownloader())
    context.set_center(staticmaps.create_latlng(48, 8))
    context.render_svg(200, 100)
    assert context.determine_center_zoom(200, 100) == (staticmaps.create_latlng(48, 8), 15)
