# py-staticmaps
# Copyright (c) 2020 Florian Pigorsch; see /LICENSE for licensing information

import typing

from PIL import Image as PIL_Image  # type: ignore
from PIL import ImageDraw as PIL_ImageDraw  # type: ignore
import s2sphere  # type: ignore

from .cairo_renderer import CairoRenderer
from .color import Color, RED, TRANSPARENT
from .line import Line
from .pillow_renderer import PillowRenderer
from .svg_renderer import SvgRenderer


class Area(Line):
    """Render an area using different renderers

    :param master: A line object
    """

    def __init__(
        self, latlngs: typing.List[s2sphere.LatLng], fill_color: Color = RED, color: Color = TRANSPARENT, width: int = 0
    ) -> None:
        Line.__init__(self, latlngs, color, width)
        if latlngs is None or len(latlngs) < 3:
            raise ValueError("Trying to create area with less than 3 coordinates")

        self._fill_color = fill_color

    def fill_color(self) -> Color:
        """Return fill color of the area

        :return: color object
        :rtype: Color
        """
        return self._fill_color

    def render_pillow(self, renderer: PillowRenderer) -> None:
        """Render area using PILLOW

        :param renderer: pillow renderer
        :type renderer: PillowRenderer
        """
        xys = [
            (x + renderer.offset_x(), y)
            for (x, y) in [renderer.transformer().ll2pixel(latlng) for latlng in self.interpolate()]
        ]
        overlay = PIL_Image.new("RGBA", renderer.image().size, (255, 255, 255, 0))
        draw = PIL_ImageDraw.Draw(overlay)
        draw.polygon(xys, fill=self.fill_color().int_rgba())
        renderer.alpha_compose(overlay)
        if self.width() > 0:
            renderer.draw().line(xys, fill=self.color().int_rgba(), width=self.width())

    def render_svg(self, renderer: SvgRenderer) -> None:
        """Render area using svgwrite

        :param renderer: svg renderer
        :type renderer: SvgRenderer
        """
        xys = [renderer.transformer().ll2pixel(latlng) for latlng in self.interpolate()]

        polygon = renderer.drawing().polygon(
            xys,
            fill=self.fill_color().hex_rgb(),
            opacity=self.fill_color().float_a(),
        )
        renderer.group().add(polygon)

        if self.width() > 0:
            polyline = renderer.drawing().polyline(
                xys,
                fill="none",
                stroke=self.color().hex_rgb(),
                stroke_width=self.width(),
                opacity=self.color().float_a(),
            )
            renderer.group().add(polyline)

    def render_cairo(self, renderer: CairoRenderer) -> None:
        """Render area using cairo

        :param renderer: cairo renderer
        :type renderer: CairoRenderer
        """
        xys = [renderer.transformer().ll2pixel(latlng) for latlng in self.interpolate()]

        renderer.context().set_source_rgba(*self.fill_color().float_rgba())
        renderer.context().new_path()
        for x, y in xys:
            renderer.context().line_to(x, y)
        renderer.context().fill()

        if self.width() > 0:
            renderer.context().set_source_rgba(*self.color().float_rgba())
            renderer.context().set_line_width(self.width())
            renderer.context().new_path()
            for x, y in xys:
                renderer.context().line_to(x, y)
            renderer.context().stroke()
