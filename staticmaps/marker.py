import math
import typing

import cairo
import s2sphere as s2  # type: ignore

from .color import text_color, ColorT
from .object import Object, PixelBoundsT
from .transformer import Transformer


class Marker(Object):
    def __init__(self, latlng: s2.LatLng, color: ColorT = (1, 0, 0), size: int = 10) -> None:
        Object.__init__(self)
        self.latlng = latlng
        self.color = color
        self.size = size

    def bounds(self) -> s2.LatLngRect:
        return s2.LatLngRect.from_point(self.latlng)

    def extra_pixel_bounds(self) -> PixelBoundsT:
        return -1 * self.size, -3 * self.size, self.size, 0

    def render(self, transformer: Transformer, cairo_context: cairo.Context) -> None:
        x, y = transformer.ll2pixel(self.latlng)
        r = self.size
        dx = math.sin(math.pi / 3.0)
        dy = math.cos(math.pi / 3.0)
        x_count = math.ceil(transformer.image_width() / (2 * transformer.world_width()))
        for p in range(-x_count, x_count + 1):
            cairo_context.save()

            cairo_context.translate(p * transformer.world_width(), 0)

            cairo_context.set_source_rgb(*text_color(self.color))
            cairo_context.arc(x, y - 2 * r, r, 0, 2 * math.pi)
            cairo_context.fill()
            cairo_context.new_path()
            cairo_context.line_to(x, y)
            cairo_context.line_to(x - dx * r, y - 2 * r + dy * r)
            cairo_context.line_to(x + dx * r, y - 2 * r + dy * r)
            cairo_context.close_path()
            cairo_context.fill()

            cairo_context.set_source_rgb(*self.color)
            cairo_context.arc(x, y - 2 * r, r - 1, 0, 2 * math.pi)
            cairo_context.fill()
            cairo_context.new_path()
            cairo_context.line_to(x, y - 1)
            cairo_context.line_to(x - dx * (r - 1), y - 2 * r + dy * (r - 1))
            cairo_context.line_to(x + dx * (r - 1), y - 2 * r + dy * (r - 1))
            cairo_context.close_path()
            cairo_context.fill()

            cairo_context.restore()
