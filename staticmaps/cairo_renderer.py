# py-staticmaps
# Copyright (c) 2020 Florian Pigorsch; see /LICENSE for licensing information

import io
import math
import typing

import cairo  # type: ignore
from PIL import Image  # type: ignore

from .area import Area
from .color import Color, BLACK, WHITE
from .line import Line
from .marker import Marker
from .renderer import Renderer
from .transformer import Transformer


class CairoRenderer(Renderer):
    def __init__(self, transformer: Transformer) -> None:
        Renderer.__init__(self, transformer)

        self._surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, *self._trans.image_size())
        self._context = cairo.Context(self._surface)

    def image_surface(self) -> cairo.ImageSurface:
        return self._surface

    def render_background(self, color: typing.Optional[Color]) -> None:
        if color is None:
            return
        self._context.set_source_rgb(*color.float_rgb())
        self._context.rectangle(0, 0, *self._trans.image_size())
        self._context.fill()

    def render_tiles(self, download: typing.Callable[[int, int, int], typing.Optional[bytes]]) -> None:
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
                    self._context.save()
                    self._context.translate(
                        xx * self._trans.tile_size() + self._trans.tile_offset_x(),
                        yy * self._trans.tile_size() + self._trans.tile_offset_y(),
                    )
                    self._context.set_source_surface(tile_img)
                    self._context.paint()
                    self._context.restore()
                except RuntimeError:
                    pass

    def render_marker_object(self, marker: Marker) -> None:
        x, y = self._trans.ll2pixel(marker.latlng())
        r = marker.size()
        dx = math.sin(math.pi / 3.0)
        dy = math.cos(math.pi / 3.0)
        x_count = math.ceil(self._trans.image_width() / (2 * self._trans.world_width()))
        for p in range(-x_count, x_count + 1):
            self._context.save()

            self._context.translate(p * self._trans.world_width(), 0)

            self._context.set_source_rgb(*marker.color().text_color().float_rgb())
            self._context.arc(x, y - 2 * r, r, 0, 2 * math.pi)
            self._context.fill()
            self._context.new_path()
            self._context.line_to(x, y)
            self._context.line_to(x - dx * r, y - 2 * r + dy * r)
            self._context.line_to(x + dx * r, y - 2 * r + dy * r)
            self._context.close_path()
            self._context.fill()

            self._context.set_source_rgb(*marker.color().float_rgb())
            self._context.arc(x, y - 2 * r, r - 1, 0, 2 * math.pi)
            self._context.fill()
            self._context.new_path()
            self._context.line_to(x, y - 1)
            self._context.line_to(x - dx * (r - 1), y - 2 * r + dy * (r - 1))
            self._context.line_to(x + dx * (r - 1), y - 2 * r + dy * (r - 1))
            self._context.close_path()
            self._context.fill()

            self._context.restore()

    def render_line_object(self, line: Line) -> None:
        if line.width() == 0:
            return
        xys = [self._trans.ll2pixel(latlng) for latlng in line.interpolate()]
        x_count = math.ceil(self._trans.image_width() / (2 * self._trans.world_width()))
        for p in range(-x_count, x_count + 1):
            self._context.save()
            self._context.translate(p * self._trans.world_width(), 0)
            self._context.set_source_rgba(*line.color().float_rgba())
            self._context.set_line_width(line.width())
            self._context.new_path()
            for x, y in xys:
                self._context.line_to(x, y)
            self._context.stroke()
            self._context.restore()

    def render_area_object(self, area: Area) -> None:
        xys = [self._trans.ll2pixel(latlng) for latlng in area.interpolate()]
        x_count = math.ceil(self._trans.image_width() / (2 * self._trans.world_width()))
        for p in range(-x_count, x_count + 1):
            self._context.save()
            self._context.translate(p * self._trans.world_width(), 0)
            self._context.new_path()
            for x, y in xys:
                self._context.line_to(x, y)
            self._context.set_source_rgba(*area.fill_color().float_rgba())
            self._context.fill()
            self._context.restore()
        self.render_line_object(area)

    def render_attribution(self, attribution: typing.Optional[str]) -> None:
        if (attribution is None) or (attribution == ""):
            return
        width, height = self._trans.image_size()
        self._context.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        font_size = 12.0
        while True:
            self._context.set_font_size(font_size)
            _, f_descent, f_height, _, _ = self._context.font_extents()
            t_width = self._context.text_extents(attribution)[3]
            if t_width < width - 4:
                break
            font_size = font_size - 0.25
        self._context.set_source_rgba(*WHITE.float_rgb(), 0.4)
        self._context.rectangle(0, height - f_height - f_descent - 2, width, height)
        self._context.fill()

        self._context.set_source_rgb(*BLACK.float_rgb())
        self._context.move_to(4, height - f_descent - 2)
        self._context.show_text(attribution)
        self._context.stroke()

    def fetch_tile(
        self, download: typing.Callable[[int, int, int], typing.Optional[bytes]], x: int, y: int
    ) -> typing.Optional[cairo.ImageSurface]:
        image_data = download(self._trans.zoom(), x, y)
        if image_data is None:
            return None
        image = Image.open(io.BytesIO(image_data))
        if image.format == "PNG":
            return cairo.ImageSurface.create_from_png(io.BytesIO(image_data))
        png_bytes = io.BytesIO()
        image.save(png_bytes, format="PNG")
        png_bytes.flush()
        png_bytes.seek(0)
        return cairo.ImageSurface.create_from_png(png_bytes)
