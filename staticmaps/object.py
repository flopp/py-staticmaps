"""py-staticmaps - object"""
# Copyright (c) 2020 Florian Pigorsch; see /LICENSE for licensing information

import typing
from abc import ABC, abstractmethod

import s2sphere  # type: ignore

from .cairo_renderer import CairoRenderer
from .pillow_renderer import PillowRenderer
from .svg_renderer import SvgRenderer
from .transformer import Transformer

PixelBoundsT = typing.Tuple[int, int, int, int]


class Object(ABC):
    """
    Object A base class for objects
    """

    def __init__(self) -> None:
        pass

    @abstractmethod
    def extra_pixel_bounds(self) -> PixelBoundsT:
        """Return extra pixel bounds from object

        Returns:
            PixelBoundsT: extra pixel bounds
        """
        return 0, 0, 0, 0

    @abstractmethod
    def bounds(self) -> s2sphere.LatLngRect:
        """Return bounds of object

        Returns:
            s2sphere.LatLngRect: bounds of object
        """
        return s2sphere.LatLngRect()

    def render_pillow(self, renderer: PillowRenderer) -> None:
        """Render object using PILLOW

        Parameters:
            renderer (PillowRenderer): pillow renderer

        Raises:
            RuntimeError: raises runtime error if a not implemented method is called
        """
        # pylint: disable=unused-argument
        t = "Pillow"
        c = type(self).__name__
        m = "render_pillow"
        raise RuntimeError(f"Cannot render to {t} since the class '{c}' doesn't implement the '{m}' method.")

    def render_svg(self, renderer: SvgRenderer) -> None:
        """Render object using svgwrite

        Parameters:
            renderer (SvgRenderer): svg renderer

        Raises:
            RuntimeError: raises runtime error if a not implemented method is called
        """
        # pylint: disable=unused-argument
        t = "SVG"
        c = type(self).__name__
        m = "render_svg"
        raise RuntimeError(f"Cannot render to {t} since the class '{c}' doesn't implement the '{m}' method.")

    def render_cairo(self, renderer: CairoRenderer) -> None:
        """Render object using cairo

        Parameters:
            renderer (CairoRenderer): cairo renderer

        Raises:
            RuntimeError: raises runtime error if a not implemented method is called
        """
        # pylint: disable=unused-argument
        t = "Cairo"
        c = type(self).__name__
        m = "render_cairo"
        raise RuntimeError(f"Cannot render to {t} since the class '{c}' doesn't implement the '{m}' method.")

    def pixel_rect(self, trans: Transformer) -> typing.Tuple[float, float, float, float]:
        """Return the pixel rect (left, top, right, bottom) of the object when using the supplied Transformer.

        Parameters:
            trans (Transformer): transformer

        Returns:
            typing.Tuple[float, float, float, float]: pixel rectangle of object
        """
        bounds = self.bounds()
        se_x, se_y = trans.ll2pixel(bounds.get_vertex(1))
        nw_x, nw_y = trans.ll2pixel(bounds.get_vertex(3))
        l, t, r, b = self.extra_pixel_bounds()
        return nw_x - l, nw_y - t, se_x + r, se_y + b

    def bounds_epb(self, trans: Transformer) -> s2sphere.LatLngRect:
        """Return the object bounds including extra pixel bounds of the object when using the supplied Transformer.

        Parameters:
            trans (Transformer): transformer

        Returns:
            s2sphere.LatLngRect: bounds of object
        """
        pixel_bounds = self.pixel_rect(trans)
        return s2sphere.LatLngRect.from_point_pair(
            trans.pixel2ll(pixel_bounds[0], pixel_bounds[1]), trans.pixel2ll(pixel_bounds[2], pixel_bounds[3])
        )
