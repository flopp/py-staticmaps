import math

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

    def render(self, transformer: Transformer, draw: svgwrite.Drawing, group: svgwrite.container.Group) -> None:
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
