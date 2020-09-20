# py-staticmaps
# Copyright (c) 2020 Florian Pigorsch; see /LICENSE for licensing information

import base64
import math
import typing

import svgwrite  # type: ignore

from .area import Area
from .color import Color, BLACK, WHITE
from .line import Line
from .marker import Marker
from .renderer import Renderer
from .transformer import Transformer


class SvgRenderer(Renderer):
    def __init__(self, transformer: Transformer) -> None:
        Renderer.__init__(self, transformer)
        self._draw = svgwrite.Drawing(
            size=(f"{self._trans.image_width()}px", f"{self._trans.image_height()}px"),
            viewBox=f"0 0 {self._trans.image_width()} {self._trans.image_height()}",
        )
        clip = self._draw.defs.add(self._draw.clipPath(id="page"))
        clip.add(self._draw.rect(insert=(0, 0), size=(self._trans.image_width(), self._trans.image_height())))

    def drawing(self) -> svgwrite.Drawing:
        return self._draw

    def render_background(self, color: typing.Optional[Color]) -> None:
        if color is None:
            return
        group = self._draw.g(clip_path="url(#page)")
        group.add(self._draw.rect(insert=(0, 0), size=self._trans.image_size(), rx=None, ry=None, fill=color.hex_rgb()))
        self._draw.add(group)

    def render_tiles(self, download: typing.Callable[[int, int, int], typing.Optional[bytes]]) -> None:
        group = self._draw.g(clip_path="url(#page)")
        for yy in range(0, self._trans.tiles_y()):
            y = self._trans.first_tile_y() + yy
            if y < 0 or y >= self._trans.number_of_tiles():
                continue
            for xx in range(0, self._trans.tiles_x()):
                x = (self._trans.first_tile_x() + xx) % self._trans.number_of_tiles()
                try:
                    tile_img = self.fetch_tile(download, x, y)
                    if tile_img is None:
                        continue
                    group.add(
                        self._draw.image(
                            tile_img,
                            insert=(
                                xx * self._trans.tile_size() + self._trans.tile_offset_x(),
                                yy * self._trans.tile_size() + self._trans.tile_offset_y(),
                            ),
                            size=(self._trans.tile_size(), self._trans.tile_size()),
                        )
                    )
                except RuntimeError:
                    pass
        self._draw.add(group)

    def render_marker_object(self, marker: Marker) -> None:
        group = self._draw.g(clip_path="url(#page)")
        x, y = self._trans.ll2pixel(marker.latlng())
        r = marker.size()
        dx = math.sin(math.pi / 3.0)
        dy = math.cos(math.pi / 3.0)
        x_count = math.ceil(self._trans.image_width() / (2 * self._trans.world_width()))
        for p in range(-x_count, x_count + 1):
            path = self._draw.path(
                fill=marker.color().hex_rgb(),
                stroke=marker.color().text_color().hex_rgb(),
                stroke_width=1,
                opacity=marker.color().float_a(),
            )
            path.push(f"M {x + p * self._trans.world_width()} {y}")
            path.push(f" l {- dx * r} {- 2 * r + dy * r}")
            path.push(f" a {r} {r} 0 1 1 {2 * r * dx} 0")
            path.push("Z")
            group.add(path)
        self._draw.add(group)

    def render_line_object(self, line: Line) -> None:
        if line.width() == 0:
            return
        group = self._draw.g(clip_path="url(#page)")
        xys = [self._trans.ll2pixel(latlng) for latlng in line.interpolate()]
        x_count = math.ceil(self._trans.image_width() / (2 * self._trans.world_width()))
        for p in range(-x_count, x_count + 1):
            polyline = self._draw.polyline(
                [(x + p * self._trans.world_width(), y) for x, y in xys],
                fill="none",
                stroke=line.color().hex_rgb(),
                stroke_width=line.width(),
                opacity=line.color().float_a(),
            )
            group.add(polyline)
        self._draw.add(group)

    def render_area_object(self, area: Area) -> None:
        group = self._draw.g(clip_path="url(#page)")
        self._draw.add(group)
        xys = [self._trans.ll2pixel(latlng) for latlng in area.interpolate()]
        x_count = math.ceil(self._trans.image_width() / (2 * self._trans.world_width()))
        for p in range(-x_count, x_count + 1):
            polygon = self._draw.polygon(
                [(x + p * self._trans.world_width(), y) for x, y in xys],
                fill=area.fill_color().hex_rgb(),
                opacity=area.fill_color().float_a(),
            )
            group.add(polygon)
        self._draw.add(group)
        self.render_line_object(area)

    def render_attribution(self, attribution: typing.Optional[str]) -> None:
        if (attribution is None) or (attribution == ""):
            return
        group = self._draw.g(clip_path="url(#page)")
        group.add(
            self._draw.rect(
                insert=(0, self._trans.image_height() - 12),
                size=(self._trans.image_width(), 12),
                rx=None,
                ry=None,
                fill=WHITE.hex_rgb(),
                fill_opacity="0.6",
            )
        )
        group.add(
            self._draw.text(
                attribution,
                insert=(2, self._trans.image_height() - 3),
                font_family="Arial, Helvetica, sans-serif",
                font_size="9px",
                fill=BLACK.hex_rgb(),
            )
        )
        self._draw.add(group)

    def fetch_tile(
        self, download: typing.Callable[[int, int, int], typing.Optional[bytes]], x: int, y: int
    ) -> typing.Optional[str]:
        image_data = download(self._trans.zoom(), x, y)
        if image_data is None:
            return None
        image_type = self.guess_image_mime_type(image_data)
        return f"data:{image_type};base64,{base64.b64encode(image_data).decode('utf-8')}"

    @staticmethod
    def guess_image_mime_type(data: bytes) -> str:
        if data[:4] == b"\xff\xd8\xff\xe0" and data[6:11] == b"JFIF\0":
            return "image/jpeg"
        if data[1:4] == b"PNG":
            return "image/png"
        return "image/png"
