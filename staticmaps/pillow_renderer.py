# py-staticmaps
# Copyright (c) 2021 Florian Pigorsch; see /LICENSE for licensing information

import io
import math
import typing

from PIL import Image as PIL_Image  # type: ignore
from PIL import ImageDraw as PIL_ImageDraw  # type: ignore

from .color import Color
from .renderer import Renderer
from .transformer import Transformer

if typing.TYPE_CHECKING:
    # avoid circlic import
    from .object import Object  # pylint: disable=cyclic-import


class PillowRenderer(Renderer):
    def __init__(self, transformer: Transformer) -> None:
        Renderer.__init__(self, transformer)
        self._image = PIL_Image.new("RGBA", (self._trans.image_width(), self._trans.image_height()))
        self._draw = PIL_ImageDraw.Draw(self._image)
        self._offset_x = 0

    def draw(self) -> PIL_ImageDraw.Draw:
        return self._draw

    def image(self) -> PIL_Image.Image:
        return self._image

    def offset_x(self) -> int:
        return self._offset_x

    def alpha_compose(self, image: PIL_Image.Image, position: typing.Tuple[int, int]) -> None:
        image2 = PIL_Image.new("RGBA", self._image.size)
        image2.paste(image, position, mask=image)
        self._image = PIL_Image.alpha_composite(self._image, image2)
        self._draw = PIL_ImageDraw.Draw(self._image)

    def render_objects(self, objects: typing.List["Object"]) -> None:
        x_count = math.ceil(self._trans.image_width() / (2 * self._trans.world_width()))
        for obj in objects:
            for p in range(-x_count, x_count + 1):
                self._offset_x = p * self._trans.world_width()
                obj.render_pillow(self)

    def render_background(self, color: typing.Optional[Color]) -> None:
        if color is None:
            return
        self.draw().rectangle([(0, 0), self.image().size], fill=color.int_rgba())

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
                    self._image.paste(
                        tile_img,
                        (
                            int(xx * self._trans.tile_size() + self._trans.tile_offset_x()),
                            int(yy * self._trans.tile_size() + self._trans.tile_offset_y()),
                        ),
                    )
                except RuntimeError:
                    pass

    def render_attribution(self, attribution: typing.Optional[str]) -> None:
        if (attribution is None) or (attribution == ""):
            return
        margin = 2
        _, th = self.draw().textsize(attribution)
        w = self._trans.image_width()
        h = self._trans.image_height()
        overlay = PIL_Image.new("RGBA", (w, h), (255, 255, 255, 0))
        draw = PIL_ImageDraw.Draw(overlay)
        draw.rectangle([(0, h - th - 2 * margin), (w, h)], fill=(255, 255, 255, 230))
        self.alpha_compose(overlay, (0, 0))
        self.draw().text((margin, h - th - margin), attribution, fill=(0, 0, 0, 255))

    def fetch_tile(
        self, download: typing.Callable[[int, int, int], typing.Optional[bytes]], x: int, y: int
    ) -> typing.Optional[PIL_Image.Image]:
        image_data = download(self._trans.zoom(), x, y)
        if image_data is None:
            return None
        return PIL_Image.open(io.BytesIO(image_data))

    @staticmethod
    def create_image(image_data: bytes) -> PIL_Image:
        return PIL_Image.open(io.BytesIO(image_data)).convert("RGBA")
