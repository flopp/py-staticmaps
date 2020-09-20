# py-staticmaps
# Copyright (c) 2020 Florian Pigorsch; see /LICENSE for licensing information

import typing

import s2sphere  # type: ignore

from .color import Color, RED, TRANSPARENT
from .line import Line
from .renderer import Renderer


class Area(Line):
    def __init__(
        self, latlngs: typing.List[s2sphere.LatLng], fill_color: Color = RED, color: Color = TRANSPARENT, width: int = 0
    ) -> None:
        Line.__init__(self, latlngs, color, width)
        if latlngs is None or len(latlngs) < 3:
            raise ValueError("Trying to create area with less than 3 coordinates")

        self._fill_color = fill_color

    def fill_color(self) -> Color:
        return self._fill_color

    def render(self, renderer: Renderer) -> None:
        renderer.render_area_object(self)
