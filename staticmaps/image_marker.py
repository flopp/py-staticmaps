# py-staticmaps
# Copyright (c) 2020 Florian Pigorsch; see /LICENSE for licensing information

import io
import typing

import s2sphere  # type: ignore
from PIL import Image as PIL_Image  # type: ignore

from .cairo_renderer import CairoRenderer
from .object import Object, PixelBoundsT
from .pillow_renderer import PillowRenderer
from .svg_renderer import SvgRenderer


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

    def render_pillow(self, renderer: PillowRenderer) -> None:
        x, y = renderer.transformer().ll2pixel(self.latlng())
        image = renderer.create_image(self.image_data())
        renderer.alpha_compose(
            image,
            (
                int(x - self.origin_x() + renderer.offset_x()),
                int(y - self.origin_y()),
            ),
        )

    def render_svg(self, renderer: SvgRenderer) -> None:
        x, y = renderer.transformer().ll2pixel(self.latlng())
        image = renderer.create_inline_image(self.image_data())

        renderer.group().add(
            renderer.drawing().image(
                image,
                insert=(x - self.origin_x(), y - self.origin_y()),
                size=(self.width(), self.height()),
            )
        )

    def render_cairo(self, renderer: CairoRenderer) -> None:
        x, y = renderer.transformer().ll2pixel(self.latlng())
        image = renderer.create_image(self.image_data())

        renderer.context().translate(x - self.origin_x(), y - self.origin_y())
        renderer.context().set_source_surface(image)
        renderer.context().paint()

    def load_image_data(self) -> None:
        with open(self._png_file, "rb") as f:
            self._image_data = f.read()
        image = PIL_Image.open(io.BytesIO(self._image_data))
        self._width, self._height = image.size
