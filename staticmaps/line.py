"""py-staticmaps - line"""
# Copyright (c) 2020 Florian Pigorsch; see /LICENSE for licensing information

import math
import typing

from geographiclib.geodesic import Geodesic  # type: ignore
import s2sphere  # type: ignore

from .color import Color, RED
from .coordinates import create_latlng
from .object import Object, PixelBoundsT
from .cairo_renderer import CairoRenderer
from .pillow_renderer import PillowRenderer
from .svg_renderer import SvgRenderer


class Line(Object):
    """
    Line A line object
    """

    def __init__(self, latlngs: typing.List[s2sphere.LatLng], color: Color = RED, width: int = 2) -> None:
        Object.__init__(self)
        if latlngs is None or len(latlngs) < 2:
            raise ValueError("Trying to create line with less than 2 coordinates")
        if width < 0:
            raise ValueError(f"'width' must be >= 0: {width}")

        self._latlngs = latlngs
        self._color = color
        self._width = width
        self._interpolation_cache: typing.Optional[typing.List[s2sphere.LatLng]] = None

    def color(self) -> Color:
        """Return color of the line

        Returns:
            Color: color object
        """
        return self._color

    def width(self) -> int:
        """Return width of line

        Returns:
            int: width
        """
        return self._width

    def bounds(self) -> s2sphere.LatLngRect:
        """Return bounds of line

        Returns:
            s2sphere.LatLngRect: bounds of line
        """
        b = s2sphere.LatLngRect()
        for latlng in self.interpolate():
            b = b.union(s2sphere.LatLngRect.from_point(latlng.normalized()))
        return b

    def extra_pixel_bounds(self) -> PixelBoundsT:
        """Return extra pixel bounds from line

        Returns:
            PixelBoundsT: extra pixel bounds
        """
        return self._width, self._width, self._width, self._width

    def interpolate(self) -> typing.List[s2sphere.LatLng]:
        """Interpolate bounds

        Returns:
            typing.List[s2sphere.LatLng]: list of LatLng
        """
        if self._interpolation_cache is not None:
            return self._interpolation_cache
        assert len(self._latlngs) >= 2
        self._interpolation_cache = []
        threshold = 2 * math.pi / 360
        last = self._latlngs[0]
        self._interpolation_cache.append(last)
        geod = Geodesic.WGS84
        for current in self._latlngs[1:]:
            # don't perform geodesic interpolation if the longitudinal distance is < threshold = 1°
            dlng = current.lng().radians - last.lng().radians
            while dlng < 0:
                dlng += 2 * math.pi
            while dlng >= math.pi:
                dlng -= 2 * math.pi
            if abs(dlng) < threshold:
                self._interpolation_cache.append(current)
                last = current
                continue
            # geodesic interpolation
            line = geod.InverseLine(
                last.lat().degrees,
                last.lng().degrees,
                current.lat().degrees,
                current.lng().degrees,
            )
            n = 2 + math.ceil(line.a13)
            for i in range(1, n):
                a = (i * line.a13) / n
                g = line.ArcPosition(a, Geodesic.LATITUDE | Geodesic.LONGITUDE | Geodesic.LONG_UNROLL)
                self._interpolation_cache.append(create_latlng(g["lat2"], g["lon2"]))
            self._interpolation_cache.append(current)
            last = current
        return self._interpolation_cache

    def render_pillow(self, renderer: PillowRenderer) -> None:
        """Render line using PILLOW

        Parameters:
            renderer (PillowRenderer): pillow renderer
        """
        if self.width() == 0:
            return
        xys = [
            (x + renderer.offset_x(), y)
            for (x, y) in [renderer.transformer().ll2pixel(latlng) for latlng in self.interpolate()]
        ]
        renderer.draw().line(xys, self.color().int_rgba(), self.width())

    def render_svg(self, renderer: SvgRenderer) -> None:
        """Render line using svgwrite

        Parameters:
            renderer (SvgRenderer): svg renderer
        """
        if self.width() == 0:
            return
        xys = [renderer.transformer().ll2pixel(latlng) for latlng in self.interpolate()]
        polyline = renderer.drawing().polyline(
            xys,
            fill="none",
            stroke=self.color().hex_rgb(),
            stroke_width=self.width(),
            opacity=self.color().float_a(),
        )
        renderer.group().add(polyline)

    def render_cairo(self, renderer: CairoRenderer) -> None:
        """Render line using cairo

        Parameters:
            renderer (CairoRenderer): cairo renderer
        """
        if self.width() == 0:
            return
        xys = [renderer.transformer().ll2pixel(latlng) for latlng in self.interpolate()]
        renderer.context().set_source_rgba(*self.color().float_rgba())
        renderer.context().set_line_width(self.width())
        renderer.context().new_path()
        for x, y in xys:
            renderer.context().line_to(x, y)
        renderer.context().stroke()
