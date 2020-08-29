import cairo
import s2sphere as s2  # type: ignore
import typing
from .transformer import Transformer

PixelBoundsT = typing.Tuple[int, int, int, int]


class Object:
    def __init__(self) -> None:
        pass

    def extra_pixel_bounds(self) -> PixelBoundsT:
        return 0, 0, 0, 0

    def bounds(self) -> s2.LatLngRect:
        return s2.LatLngRect()

    def render(self, transformer: Transformer, cairo_context: cairo.Context) -> None:
        print("render object")
