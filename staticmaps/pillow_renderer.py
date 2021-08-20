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
    """An image renderer using pillow that extends a generic renderer class"""

    def __init__(self, transformer: Transformer) -> None:
        Renderer.__init__(self, transformer)
        self._image = PIL_Image.new("RGBA", (self._trans.image_width(), self._trans.image_height()))
        self._draw = PIL_ImageDraw.Draw(self._image)
        self._offset_x = 0

        # save the maximum and minimum x and y coordinates of the rendered objects
        self._obj_x_min = None
        self._obj_x_max = None
        self._obj_y_min = None
        self._obj_y_max = None

    def draw(self) -> PIL_ImageDraw.Draw:
        return self._draw

    def image(self) -> PIL_Image.Image:
        return self._image

    def image_tight_on_objects(self) -> PIL_Image.Image:
        """
        Make PIL image which is tight on the objects i.e not boundary between objects and edge of image.
        """
        return self._image.crop((self._obj_x_min, self._obj_y_min, self._obj_x_max, self._obj_y_max))

    def offset_x(self) -> int:
        return self._offset_x

    def alpha_compose(self, image: PIL_Image.Image) -> None:
        assert image.size == self._image.size
        self._image = PIL_Image.alpha_composite(self._image, image)
        self._draw = PIL_ImageDraw.Draw(self._image)

    def render_objects(self, objects: typing.List["Object"], render_tight_on_objects:bool = False) -> None:
        """Render all objects of static map

        :param objects: objects of static map
        :type objects: typing.List["Object"]
        """
        x_count = math.ceil(self._trans.image_width() / (2 * self._trans.world_width()))
        for obj in objects:
            for p in range(-x_count, x_count + 1):
                self._offset_x = p * self._trans.world_width()
                obj.render_pillow(self)

        if render_tight_on_objects:
            self.update_obj_x_y_min_max(objects)

    def render_background(self, color: typing.Optional[Color]) -> None:
        """Render background of static map

        :param color: background color
        :type color: typing.Optional[Color]
        """
        if color is None:
            return
        self.draw().rectangle([(0, 0), self.image().size], fill=color.int_rgba())

    def render_tiles(self, download: typing.Callable[[int, int, int], typing.Optional[bytes]]) -> None:
        """Render background of static map

        :param download: url of tiles provider
        :type download: typing.Callable[[int, int, int], typing.Optional[bytes]]
        """
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
        """Render attribution from given tiles provider

        :param attribution: Attribution for the given tiles provider
        :type attribution: typing.Optional[str]:
        """
        if (attribution is None) or (attribution == ""):
            return
        margin = 2
        _, th = self.draw().textsize(attribution)
        w = self._trans.image_width()
        h = self._trans.image_height()
        overlay = PIL_Image.new("RGBA", self._image.size, (255, 255, 255, 0))
        draw = PIL_ImageDraw.Draw(overlay)
        draw.rectangle([(0, h - th - 2 * margin), (w, h)], fill=(255, 255, 255, 204))
        self.alpha_compose(overlay)
        self.draw().text((margin, h - th - margin), attribution, fill=(0, 0, 0, 255))

    def fetch_tile(
        self, download: typing.Callable[[int, int, int], typing.Optional[bytes]], x: int, y: int
    ) -> typing.Optional[PIL_Image.Image]:
        """Fetch tiles from given tiles provider

        :param download: callable
        :param x: width
        :param y: height
        :type download: typing.Callable[[int, int, int], typing.Optional[bytes]]
        :type x: int
        :type y: int

        :return: pillow image
        :rtype: typing.Optional[PIL_Image.Image]
        """
        image_data = download(self._trans.zoom(), x, y)
        if image_data is None:
            return None
        return PIL_Image.open(io.BytesIO(image_data))

    @staticmethod
    def create_image(image_data: bytes) -> PIL_Image:
        """Create a pillow image

        :param image_data: Image data
        :type image_data: bytes

        :return: pillow image
        :rtype: PIL.Image
        """
        return PIL_Image.open(io.BytesIO(image_data)).convert("RGBA")

    def update_obj_x_y_min_max(self, objects: typing.List["Object"]):
        """
        Update x and y, min and max coorindates from all objects.
        """

        for obj in objects:

            # this probably only works for class Marker
            x, y = self.transformer().ll2pixel(obj.latlng())

            self._obj_x_min = x if self._obj_x_min is None else min(x,self._obj_x_min)
            self._obj_x_max = x if self._obj_x_max is None else max(x, self._obj_x_max)
            self._obj_y_min = y if self._obj_y_min is None else min(y, self._obj_y_min)
            self._obj_y_max = y if self._obj_y_max is None else max(y, self._obj_y_max)
