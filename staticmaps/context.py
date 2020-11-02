# py-staticmaps
# Copyright (c) 2020 Florian Pigorsch; see /LICENSE for licensing information

import math
import os
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
        if b is None:
            return self._center, self._clamp_zoom(self._zoom)
        if self._zoom is not None:
            return b.get_center(), self._clamp_zoom(self._zoom)
        if self._center is not None:
            b = b.union(s2sphere.LatLngRect(self._center, self._center))
        if b.is_point():
            return b.get_center(), None
        pixel_margin = self.extra_pixel_bounds()
        w = (width - 2.0 * max(pixel_margin[0], pixel_margin[2])) / self._tile_provider.tile_size()
        h = (height - 2.0 * max(pixel_margin[1], pixel_margin[3])) / self._tile_provider.tile_size()
        min_y = (1.0 - math.log(math.tan(b.lat_lo().radians) + (1.0 / math.cos(b.lat_lo().radians)))) / (2 * math.pi)
        max_y = (1.0 - math.log(math.tan(b.lat_hi().radians) + (1.0 / math.cos(b.lat_hi().radians)))) / (2 * math.pi)
        dx = (b.lng_hi().degrees - b.lng_lo().degrees) / 360.0
        if dx < 0:
            dx += math.ceil(math.fabs(dx))
        if dx > 1:
            dx -= math.floor(dx)
        dy = math.fabs(max_y - min_y)

        y1 = math.log((1 + math.sin(b.lat_lo().radians)) / (1 - math.sin(b.lat_lo().radians))) / 2
        y2 = math.log((1 + math.sin(b.lat_hi().radians)) / (1 - math.sin(b.lat_hi().radians))) / 2
        lat = math.atan(math.sinh((y1 + y2) / 2)) * 180.0 / math.pi
        lng = b.get_center().lng().degrees
        center = s2sphere.LatLng.from_degrees(lat, lng)

        for zoom in range(1, self._tile_provider.max_zoom()):
            tiles = 2 ** zoom
            if (dx * tiles > w) or(dy * tiles > h):
                return center, zoom - 1
        return center, self._tile_provider.max_zoom()

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
