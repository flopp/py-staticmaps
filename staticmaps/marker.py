"""py-staticmaps - marker"""
# Copyright (c) 2020 Florian Pigorsch; see /LICENSE for licensing information

import math

import s2sphere  # type: ignore

from .cairo_renderer import CairoRenderer
from .color import RED, Color
from .object import Object, PixelBoundsT
from .pillow_renderer import PillowRenderer
from .svg_renderer import SvgRenderer


class Marker(Object):
    """
    Marker A marker object
    """

    def __init__(self, latlng: s2sphere.LatLng, color: Color = RED, size: int = 10) -> None:
        Object.__init__(self)
        self._latlng = latlng
        self._color = color
        self._size = size

    def latlng(self) -> s2sphere.LatLng:
        """Return LatLng of the marker

        Returns:
            s2sphere.LatLng: LatLng of the marker
        """
        return self._latlng

    def color(self) -> Color:
        """Return color of the marker

        Returns:
            Color: color object
        """
        return self._color

    def size(self) -> int:
        """Return size of the marker

        Returns:
            int: size of the marker
        """
        return self._size

    def bounds(self) -> s2sphere.LatLngRect:
        """Return bounds of the marker

        Returns:
            s2sphere.LatLngRect: bounds of the marker
        """
        return s2sphere.LatLngRect.from_point(self._latlng)

    def extra_pixel_bounds(self) -> PixelBoundsT:
        """Return extra pixel bounds of the marker

        Returns:
            PixelBoundsT: extra pixel bounds of the marker
        """
        return self._size, self._size, self._size, 0

    def render_pillow(self, renderer: PillowRenderer) -> None:
        """Render marker using PILLOW

        Parameters:
            renderer (PillowRenderer): pillow renderer
        """
        x, y = renderer.transformer().ll2pixel(self.latlng())
        x += renderer.offset_x()

        r = self.size()
        dx = math.sin(math.pi / 3.0)
        dy = math.cos(math.pi / 3.0)
        cy = y - 2 * r

        renderer.draw().chord([(x - r, cy - r), (x + r, cy + r)], 150, 30, fill=self.color().text_color().int_rgba())
        renderer.draw().polygon(
            [(x, y), (x - dx * r, cy + dy * r), (x + dx * r, cy + dy * r)], fill=self.color().text_color().int_rgba()
        )

        renderer.draw().polygon(
            [(x, y - 1), (x - dx * (r - 1), cy + dy * (r - 1)), (x + dx * (r - 1), cy + dy * (r - 1))],
            fill=self.color().int_rgba(),
        )
        renderer.draw().chord(
            [(x - (r - 1), cy - (r - 1)), (x + (r - 1), cy + (r - 1))], 150, 30, fill=self.color().int_rgba()
        )

    def render_svg(self, renderer: SvgRenderer) -> None:
        """Render marker using svgwrite

        Parameters:
            renderer (SvgRenderer): svg renderer
        """
        x, y = renderer.transformer().ll2pixel(self.latlng())
        r = self.size()
        dx = math.sin(math.pi / 3.0)
        dy = math.cos(math.pi / 3.0)
        path = renderer.drawing().path(
            fill=self.color().hex_rgb(),
            stroke=self.color().text_color().hex_rgb(),
            stroke_width=1,
            opacity=self.color().float_a(),
        )
        path.push(f"M {x} {y}")
        path.push(f" l {- dx * r} {- 2 * r + dy * r}")
        path.push(f" a {r} {r} 0 1 1 {2 * r * dx} 0")
        path.push("Z")
        renderer.group().add(path)

    def render_cairo(self, renderer: CairoRenderer) -> None:
        """Render marker using cairo

        Parameters:
            renderer (CairoRenderer): cairo renderer
        """
        x, y = renderer.transformer().ll2pixel(self.latlng())
        r = self.size()
        dx = math.sin(math.pi / 3.0)
        dy = math.cos(math.pi / 3.0)

        renderer.context().set_source_rgb(*self.color().text_color().float_rgb())
        renderer.context().arc(x, y - 2 * r, r, 0, 2 * math.pi)
        renderer.context().fill()
        renderer.context().new_path()
        renderer.context().line_to(x, y)
        renderer.context().line_to(x - dx * r, y - 2 * r + dy * r)
        renderer.context().line_to(x + dx * r, y - 2 * r + dy * r)
        renderer.context().close_path()
        renderer.context().fill()

        renderer.context().set_source_rgb(*self.color().float_rgb())
        renderer.context().arc(x, y - 2 * r, r - 1, 0, 2 * math.pi)
        renderer.context().fill()
        renderer.context().new_path()
        renderer.context().line_to(x, y - 1)
        renderer.context().line_to(x - dx * (r - 1), y - 2 * r + dy * (r - 1))
        renderer.context().line_to(x + dx * (r - 1), y - 2 * r + dy * (r - 1))
        renderer.context().close_path()
        renderer.context().fill()
