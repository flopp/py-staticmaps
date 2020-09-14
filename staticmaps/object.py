from abc import ABC, abstractmethod
import typing

import cairo  # type: ignore
import svgwrite  # type: ignore
import s2sphere  # type: ignore
from .transformer import Transformer

PixelBoundsT = typing.Tuple[int, int, int, int]


class Object(ABC):
    def __init__(self) -> None:
        pass

    @abstractmethod
    def extra_pixel_bounds(self) -> PixelBoundsT:
        return 0, 0, 0, 0

    @abstractmethod
    def bounds(self) -> s2sphere.LatLngRect:
        return s2sphere.LatLngRect()

    @abstractmethod
    def render_image(self, transformer: Transformer, cairo_context: cairo.Context) -> None:
        raise NotImplementedError("render_image is not implemented")

    @abstractmethod
    def render_svg(self, transformer: Transformer, draw: svgwrite.Drawing, group: svgwrite.container.Group) -> None:
        raise NotImplementedError("render_svg is not implemented")
