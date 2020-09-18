# py-staticmaps
# Copyright (c) 2020 Florian Pigorsch; see /LICENSE for licensing information

import s2sphere  # type: ignore

from .color import Color, RED
from .object import Object, PixelBoundsT
from .renderer import Renderer


class Marker(Object):
    def __init__(self, latlng: s2sphere.LatLng, color: Color = RED, size: int = 10) -> None:
        Object.__init__(self)
        self._latlng = latlng
        self._color = color
        self._size = size

    def latlng(self) -> s2sphere.LatLng:
        return self._latlng

    def color(self) -> Color:
        return self._color

    def size(self) -> int:
        return self._size

    def bounds(self) -> s2sphere.LatLngRect:
        return s2sphere.LatLngRect.from_point(self._latlng)

    def extra_pixel_bounds(self) -> PixelBoundsT:
        return self._size, self._size, self._size, 0

    def render(self, renderer: Renderer) -> None:
        renderer.render_marker_object(self)
