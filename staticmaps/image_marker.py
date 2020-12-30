# py-staticmaps
# Copyright (c) 2020 Florian Pigorsch; see /LICENSE for licensing information

import io
import typing

import s2sphere  # type: ignore
from PIL import Image  # type: ignore

from .object import Object, PixelBoundsT
from .renderer import Renderer


class ImageMarker(Object):
    def __init__(self, latlng: s2sphere.LatLng, png_file: str, origin_x: int, origin_y: int) -> None:
        Object.__init__(self)
        self._latlng = latlng
        self._png_file = png_file
        self._origin_x = origin_x
        self._origin_y = origin_y
        self._width = 0
        self._height = 0
        self._image_data: typing.Optional[bytes] = None

    def origin_x(self) -> int:
        return self._origin_x

    def origin_y(self) -> int:
        return self._origin_y

    def width(self) -> int:
        if self._image_data is None:
            self.load_image_data()
        return self._width

    def height(self) -> int:
        if self._image_data is None:
            self.load_image_data()
        return self._height

    def image_data(self) -> bytes:
        if self._image_data is None:
            self.load_image_data()
        assert self._image_data
        return self._image_data

    def latlng(self) -> s2sphere.LatLng:
        return self._latlng

    def bounds(self) -> s2sphere.LatLngRect:
        return s2sphere.LatLngRect.from_point(self._latlng)

    def extra_pixel_bounds(self) -> PixelBoundsT:
        return (
            max(0, self._origin_x),
            max(0, self._origin_y),
            max(0, self.width() - self._origin_x),
            max(0, self.height() - self._origin_y),
        )

    def render(self, renderer: Renderer) -> None:
        renderer.render_image_marker_object(self)

    def load_image_data(self) -> None:
        with open(self._png_file, "rb") as f:
            self._image_data = f.read()
        image = Image.open(io.BytesIO(self._image_data))
        self._width, self._height = image.size
