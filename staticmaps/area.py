# py-staticmaps
# Copyright (c) 2020 Florian Pigorsch; see /LICENSE for licensing information

import typing

from PIL import Image as PIL_Image  # type: ignore
from PIL import ImageDraw as PIL_ImageDraw  # type: ignore
import s2sphere  # type: ignore

from .cairo_renderer import CairoRenderer
from .color import Color, RED, TRANSPARENT
from .line import Line, _draw_pillow_dashes
from .pillow_renderer import PillowRenderer
from .svg_renderer import SvgRenderer


class Area(Line):
    """Render an area using different renderers

    :param master: A line object
    """

    def __init__(
        self,
        latlngs: typing.List[s2sphere.LatLng],
        fill_color: Color = RED,
        color: Color = TRANSPARENT,
        width: int = 0,
        dash_array: typing.Optional[typing.Sequence[float]] = None,
    ) -> None:
        Line.__init__(self, latlngs, color, width, dash_array)
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
            if self.dash_array() is None:
                renderer.draw().line(xys + [xys[0]], fill=self.color().int_rgba(), width=self.width())
            else:
                bounds = (
                    -self.width(),
                    -self.width(),
                    renderer.image().width + self.width(),
                    renderer.image().height + self.width(),
                )
                _draw_pillow_dashes(
                    renderer.draw(),
                    xys,
                    self.dash_array(),
                    bounds=bounds,
                    fill=self.color().int_rgba(),
                    width=self.width(),
                    close=True,
                )

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
            dash_array = self.dash_array()
            outline = renderer.drawing().polygon(
                xys,
                fill="none",
                stroke=self.color().hex_rgb(),
                stroke_width=self.width(),
                opacity=self.color().float_a(),
                **(
                    {"stroke_dasharray": ",".join(str(length) for length in dash_array)}
                    if dash_array is not None
                    else {}
                ),
            )
            renderer.group().add(outline)

    def render_cairo(self, renderer: CairoRenderer) -> None:
        """Render area using cairo

        :param renderer: cairo renderer
        :type renderer: CairoRenderer
        """
        xys = [renderer.transformer().ll2pixel(latlng) for latlng in self.interpolate()]

        renderer.context().set_source_rgba(*self.fill_color().float_rgba())
        renderer.context().new_path()
        renderer.context().move_to(*xys[0])
        for x, y in xys[1:]:
            renderer.context().line_to(x, y)
        renderer.context().fill()

        if self.width() > 0:
            renderer.context().set_source_rgba(*self.color().float_rgba())
            renderer.context().set_line_width(self.width())
            renderer.context().set_dash(self.dash_array() or [])
            renderer.context().new_path()
            renderer.context().move_to(*xys[0])
            for x, y in xys[1:]:
                renderer.context().line_to(x, y)
            renderer.context().close_path()
            renderer.context().stroke()
