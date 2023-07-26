"""py-staticmaps - bounds"""
# Copyright (c) 2020 Florian Pigorsch; see /LICENSE for licensing information

import typing

import s2sphere  # type: ignore

from .cairo_renderer import CairoRenderer
from .object import Object, PixelBoundsT
from .pillow_renderer import PillowRenderer
from .svg_renderer import SvgRenderer


class Bounds(Object):
    """
    Custom bounds object to be respected for the final static map. Nothing is being rendered.
    """

    def __init__(
        self, latlngs: typing.List[s2sphere.LatLng], extra_pixel_bounds: typing.Union[int, PixelBoundsT] = 0
    ) -> None:
        Object.__init__(self)
        if latlngs is None or len(latlngs) < 2:
            raise ValueError("Trying to create custom bounds with less than 2 coordinates")
        self._latlngs = latlngs
        if isinstance(extra_pixel_bounds, int):
            self._extra_pixel_bounds = (extra_pixel_bounds, extra_pixel_bounds, extra_pixel_bounds, extra_pixel_bounds)
        else:
            self._extra_pixel_bounds = extra_pixel_bounds

    def bounds(self) -> s2sphere.LatLngRect:
        """Return bounds of bounds object

        Returns:
            s2sphere.LatLngRect: bounds of bounds object
        """
        b = s2sphere.LatLngRect()
        for latlng in self._latlngs:
            b = b.union(s2sphere.LatLngRect.from_point(latlng.normalized()))
        return b

    def extra_pixel_bounds(self) -> PixelBoundsT:
        """Return extra pixel bounds of bounds object

        Returns:
            PixelBoundsT: extra pixel bounds
        """
        return self._extra_pixel_bounds

    def render_pillow(self, renderer: PillowRenderer) -> None:
        """Do not render custom bounds for pillow

        Parameters:
            renderer (PillowRenderer): pillow renderer
        """
        return

    def render_svg(self, renderer: SvgRenderer) -> None:
        """Do not render custom bounds for svg

        Parameters:
            renderer (SvgRenderer): svg renderer
        """
        return

    def render_cairo(self, renderer: CairoRenderer) -> None:
        """Do not render custom bounds for cairo

        Parameters:
            renderer (CairoRenderer): cairo renderer
        """
        return
