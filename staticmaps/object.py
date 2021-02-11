# py-staticmaps
# Copyright (c) 2020 Florian Pigorsch; see /LICENSE for licensing information

from abc import ABC, abstractmethod
import typing

import s2sphere  # type: ignore

from .renderer import Renderer
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
    def render(self, renderer: Renderer) -> None:
        pass

    def pixel_rect(self, trans: Transformer) -> typing.Tuple[float, float, float, float]:
        """Return the pixel rect (left, top, right, bottom) of the object when using the supplied Transformer."""
        bounds = self.bounds()
        se_x, se_y = trans.ll2pixel(bounds.get_vertex(1))
        nw_x, nw_y = trans.ll2pixel(bounds.get_vertex(3))
        l, t, r, b = self.extra_pixel_bounds()
        return nw_x - l, nw_y - t, se_x + r, se_y + b
