import math

import cairo  # type: ignore
import s2sphere  # type: ignore
import svgwrite  # type: ignore

from .color import Color, RED
from .object import Object, PixelBoundsT
from .transformer import Transformer


class Marker(Object):
    def __init__(self, latlng: s2sphere.LatLng, color: Color = RED, size: int = 10) -> None:
        Object.__init__(self)
        self._latlng = latlng
        self._color = color
        self._size = size

    def bounds(self) -> s2sphere.LatLngRect:
        return s2sphere.LatLngRect.from_point(self._latlng)

    def extra_pixel_bounds(self) -> PixelBoundsT:
        return self._size, self._size, self._size, 0

    def render_image(self, transformer: Transformer, cairo_context: cairo.Context) -> None:
        x, y = transformer.ll2pixel(self._latlng)
        r = self._size
        dx = math.sin(math.pi / 3.0)
        dy = math.cos(math.pi / 3.0)
        x_count = math.ceil(transformer.image_width() / (2 * transformer.world_width()))
        for p in range(-x_count, x_count + 1):
            cairo_context.save()

            cairo_context.translate(p * transformer.world_width(), 0)

            cairo_context.set_source_rgba(*self._color.text_color().cairo_rgba())
            cairo_context.arc(x, y - 2 * r, r, 0, 2 * math.pi)
            cairo_context.fill()
            cairo_context.new_path()
            cairo_context.line_to(x, y)
            cairo_context.line_to(x - dx * r, y - 2 * r + dy * r)
            cairo_context.line_to(x + dx * r, y - 2 * r + dy * r)
            cairo_context.close_path()
            cairo_context.fill()

            cairo_context.set_source_rgba(*self._color.cairo_rgba())
            cairo_context.arc(x, y - 2 * r, r - 1, 0, 2 * math.pi)
            cairo_context.fill()
            cairo_context.new_path()
            cairo_context.line_to(x, y - 1)
            cairo_context.line_to(x - dx * (r - 1), y - 2 * r + dy * (r - 1))
            cairo_context.line_to(x + dx * (r - 1), y - 2 * r + dy * (r - 1))
            cairo_context.close_path()
            cairo_context.fill()

            cairo_context.restore()

    def render_svg(self, transformer: Transformer, draw: svgwrite.Drawing, group: svgwrite.container.Group) -> None:
        x, y = transformer.ll2pixel(self._latlng)
        r = self._size
        dx = math.sin(math.pi / 3.0)
        dy = math.cos(math.pi / 3.0)
        x_count = math.ceil(transformer.image_width() / (2 * transformer.world_width()))
        for p in range(-x_count, x_count + 1):
            path = draw.path(
                fill=self._color.hex_string(), stroke=self._color.text_color().hex_string(), stroke_width=1
            )
            path.push(f"M {x + p * transformer.world_width()} {y}")
            path.push(f" l {- dx * r} {- 2 * r + dy * r}")
            path.push(f" a {r} {r} 0 1 1 {2 * r * dx} 0")
            path.push("Z")
            group.add(path)
