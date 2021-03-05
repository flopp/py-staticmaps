# py-staticmaps
# Copyright (c) 2020 Florian Pigorsch; see /LICENSE for licensing information

import math
import os
import sys
import typing

import appdirs  # type: ignore
import cairo  # type: ignore
import s2sphere  # type: ignore
import svgwrite  # type: ignore

from .cairo_renderer import CairoRenderer
from .color import Color
from .meta import LIB_NAME
from .object import Object, PixelBoundsT
from .svg_renderer import SvgRenderer
from .tile_downloader import TileDownloader
from .tile_provider import TileProvider, tile_provider_OSM
from .transformer import Transformer


class Context:
    def __init__(self) -> None:
        self._background_color: typing.Optional[Color] = None
        self._objects: typing.List[Object] = []
        self._center: typing.Optional[s2sphere.LatLng] = None
        self._zoom: typing.Optional[int] = None
        self._tile_provider = tile_provider_OSM
        self._tile_downloader = TileDownloader()
        self._cache_dir = os.path.join(appdirs.user_cache_dir(LIB_NAME), "tiles")

    def set_zoom(self, zoom: int) -> None:
        if zoom < 0 or zoom > 30:
            raise ValueError("Bad zoom value: {}".format(zoom))
        self._zoom = zoom

    def set_center(self, latlng: s2sphere.LatLng) -> None:
        self._center = latlng

    def set_background_color(self, color: Color) -> None:
        self._background_color = color

    def set_cache_dir(self, directory: str) -> None:
        self._cache_dir = directory

    def set_tile_downloader(self, downloader: TileDownloader) -> None:
        self._tile_downloader = downloader

    def set_tile_provider(self, provider: TileProvider) -> None:
        self._tile_provider = provider

    def add_object(self, obj: Object) -> None:
        self._objects.append(obj)

    def render_cairo(self, width: int, height: int) -> cairo.ImageSurface:
        if "cairo" not in sys.modules:
            raise RuntimeError('You need to install the "cairo" module to enable "render_cairo".')

        center, zoom = self.determine_center_zoom(width, height)
        if center is None or zoom is None:
            raise RuntimeError("Cannot render map without center/zoom.")

        trans = Transformer(width, height, zoom, center, self._tile_provider.tile_size())

        renderer = CairoRenderer(trans)
        renderer.render_background(self._background_color)
        renderer.render_tiles(self._fetch_tile)
        renderer.render_objects(self._objects)
        renderer.render_attribution(self._tile_provider.attribution())

        return renderer.image_surface()

    def render_svg(self, width: int, height: int) -> svgwrite.Drawing:
        center, zoom = self.determine_center_zoom(width, height)
        if center is None or zoom is None:
            raise RuntimeError("Cannot render map without center/zoom.")

        trans = Transformer(width, height, zoom, center, self._tile_provider.tile_size())

        renderer = SvgRenderer(trans)
        renderer.render_background(self._background_color)
        renderer.render_tiles(self._fetch_tile)
        renderer.render_objects(self._objects)
        renderer.render_attribution(self._tile_provider.attribution())

        return renderer.drawing()

    def object_bounds(self) -> typing.Optional[s2sphere.LatLngRect]:
        if len(self._objects) == 0:
            return None
        bounds = s2sphere.LatLngRect()
        for obj in self._objects:
            bounds = bounds.union(obj.bounds())
        return bounds

    def extra_pixel_bounds(self) -> PixelBoundsT:
        max_l, max_t, max_r, max_b = 0, 0, 0, 0
        attribution = self._tile_provider.attribution()
        if (attribution is None) or (attribution == ""):
            max_b = 12
        for obj in self._objects:
            (l, t, r, b) = obj.extra_pixel_bounds()
            max_l = max(max_l, l)
            max_t = max(max_t, t)
            max_r = max(max_r, r)
            max_b = max(max_b, b)
        return (max_l, max_t, max_r, max_b)

    def determine_center_zoom(self, width: int, height: int) -> typing.Tuple[s2sphere.LatLng, typing.Optional[int]]:
        if self._center is not None:
            if self._zoom is not None:
                return self._center, self._clamp_zoom(self._zoom)
            b = self.object_bounds()
            return self._center, self._determine_zoom(width, height, b, self._center)

        b = self.object_bounds()
        if b is None:
            return None, None

        c = self._determine_center(b)
        z = self._zoom
        if z is None:
            z = self._determine_zoom(width, height, b, c)
        if z is None:
            return None, None
        return self._adjust_center(width, height, c, z), z

    def _determine_zoom(
        self, width: int, height: int, b: typing.Optional[s2sphere.LatLngRect], c: s2sphere.LatLngRect
    ) -> typing.Optional[int]:
        if b is None:
            b = s2sphere.LatLngRect(c, c)
        else:
            b = b.union(s2sphere.LatLngRect(c, c))
        if b.is_point():
            return self._clamp_zoom(15)

        pixel_margin = self.extra_pixel_bounds()

        w = (width - pixel_margin[0] - pixel_margin[2]) / self._tile_provider.tile_size()
        h = (height - pixel_margin[1] - pixel_margin[3]) / self._tile_provider.tile_size()
        # margins are bigger than target image size => ignore them
        if w <= 0 or h <= 0:
            w = width / self._tile_provider.tile_size()
            h = height / self._tile_provider.tile_size()

        min_y = (1.0 - math.log(math.tan(b.lat_lo().radians) + (1.0 / math.cos(b.lat_lo().radians)))) / (2 * math.pi)
        max_y = (1.0 - math.log(math.tan(b.lat_hi().radians) + (1.0 / math.cos(b.lat_hi().radians)))) / (2 * math.pi)
        dx = (b.lng_hi().degrees - b.lng_lo().degrees) / 360.0
        if dx < 0:
            dx += math.ceil(math.fabs(dx))
        if dx > 1:
            dx -= math.floor(dx)
        dy = math.fabs(max_y - min_y)

        for zoom in range(1, self._tile_provider.max_zoom()):
            tiles = 2 ** zoom
            if (dx * tiles > w) or (dy * tiles > h):
                return self._clamp_zoom(zoom - 1)
        return self._clamp_zoom(15)

    @staticmethod
    def _determine_center(b: s2sphere.LatLngRect) -> s2sphere.LatLng:
        y1 = math.log((1 + math.sin(b.lat_lo().radians)) / (1 - math.sin(b.lat_lo().radians))) / 2
        y2 = math.log((1 + math.sin(b.lat_hi().radians)) / (1 - math.sin(b.lat_hi().radians))) / 2
        lat = math.atan(math.sinh((y1 + y2) / 2)) * 180 / math.pi
        lng = b.get_center().lng().degrees
        return s2sphere.LatLng.from_degrees(lat, lng)

    def _adjust_center(self, width: int, height: int, center: s2sphere.LatLng, zoom: int) -> s2sphere.LatLng:
        if len(self._objects) == 0:
            return center

        trans = Transformer(width, height, zoom, center, self._tile_provider.tile_size())

        min_x = None
        max_x = None
        min_y = None
        max_y = None
        for obj in self._objects:
            l, t, r, b = obj.pixel_rect(trans)
            if min_x is None:
                min_x = l
                max_x = r
                min_y = t
                max_y = b
            else:
                min_x = min(min_x, l)
                max_x = max(max_x, r)
                min_y = min(min_y, t)
                max_y = max(max_y, b)
        assert min_x is not None
        assert max_x is not None
        assert min_y is not None
        assert max_y is not None

        # margins are bigger than the image => ignore
        if (max_x - min_x) > width or (max_y - min_y) > height:
            return center

        return trans.pixel2ll((max_x + min_x) * 0.5, (max_y + min_y) * 0.5)

    def _fetch_tile(self, z: int, x: int, y: int) -> typing.Optional[bytes]:
        return self._tile_downloader.get(self._tile_provider, self._cache_dir, z, x, y)

    def _clamp_zoom(self, zoom: typing.Optional[int]) -> typing.Optional[int]:
        if zoom is None:
            return None
        if zoom < 0:
            return 0
        if zoom > self._tile_provider.max_zoom():
            return self._tile_provider.max_zoom()
        return zoom
