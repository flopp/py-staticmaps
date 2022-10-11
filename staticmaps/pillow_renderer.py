"""py-staticmaps - pillow_renderer"""
# Copyright (c) 2021 Florian Pigorsch; see /LICENSE for licensing information

import io
import math
import typing

import s2sphere  # type: ignore
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

    def draw(self) -> PIL_ImageDraw.Draw:
        """
        draw Call PIL_ImageDraw.Draw()

        Returns:
            PIL_ImageDraw.Draw: An PIL_Image draw object
        """
        return self._draw

    def image(self) -> PIL_Image.Image:
        """
        image Call PIL_Image.new()

        Returns:
            PIL_Image.Image: A PIL_Image image object
        """
        return self._image

    def offset_x(self) -> int:
        """
        offset_x Return the offset in x direction

        Returns:
            int: Offset in x direction
        """
        return self._offset_x

    def alpha_compose(self, image: PIL_Image.Image) -> None:
        """
        alpha_compose Call PIL_Image.alpha_composite()

        Parameters:
            image (PIL_Image.Image): A PIL_Image image object
        """
        assert image.size == self._image.size
        self._image = PIL_Image.alpha_composite(self._image, image)
        self._draw = PIL_ImageDraw.Draw(self._image)

    def render_objects(
        self,
        objects: typing.List["Object"],
        bbox: s2sphere.LatLngRect = None,
        epb: typing.Tuple[int, int, int, int] = None,
    ) -> None:
        """Render all objects of static map

        Parameters:
            objects (typing.List["Object"]): objects of static map
            bbox (s2sphere.LatLngRect): boundary box of all objects
            epb (typing.Tuple[int, int, int, int]): extra pixel bounds
        """
        x_count = math.ceil(self._trans.image_width() / (2 * self._trans.world_width()))
        for obj in objects:
            for p in range(-x_count, x_count + 1):
                self._offset_x = p * self._trans.world_width()
                obj.render_pillow(self)

    def render_background(self, color: typing.Optional[Color]) -> None:
        """Render background of static map

        Parameters:
            color (typing.Optional[Color]): background color
        """
        if color is None:
            return
        self.draw().rectangle(((0, 0), self.image().size), fill=color.int_rgba())

    def render_tiles(
        self,
        download: typing.Callable[[int, int, int], typing.Optional[bytes]],
        bbox: s2sphere.LatLngRect = None,
        epb: typing.Tuple[int, int, int, int] = None,
    ) -> None:
        """Render background of static map

        Parameters:
            download (typing.Callable[[int, int, int], typing.Optional[bytes]]): url of tiles provider
            bbox (s2sphere.LatLngRect): boundary box of all objects
            epb (typing.Tuple[int, int, int, int]): extra pixel bounds
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

        Parameters:
            attribution (typing.Optional[str]:): Attribution for the given tiles provider
        """
        if (attribution is None) or (attribution == ""):
            return
        margin = 2
        _, th = self.draw().textsize(attribution)
        w = self._trans.image_width()
        h = self._trans.image_height()
        overlay = PIL_Image.new("RGBA", self._image.size, (255, 255, 255, 0))
        draw = PIL_ImageDraw.Draw(overlay)
        draw.rectangle(((0, h - th - 2 * margin), (w, h)), fill=(255, 255, 255, 204))
        self.alpha_compose(overlay)
        self.draw().text((margin, h - th - margin), attribution, fill=(0, 0, 0, 255))

    def fetch_tile(
        self, download: typing.Callable[[int, int, int], typing.Optional[bytes]], x: int, y: int
    ) -> typing.Optional[PIL_Image.Image]:
        """Fetch tiles from given tiles provider

        Parameters:
            download (typing.Callable[[int, int, int], typing.Optional[bytes]]): callable
            x (int): width
            y (int): height

        Returns:
            typing.Optional[PIL_Image.Image]: pillow image
        """
        image_data = download(self._trans.zoom(), x, y)
        if image_data is None:
            return None
        return PIL_Image.open(io.BytesIO(image_data))

    @staticmethod
    def create_image(image_data: bytes) -> PIL_Image:
        """Create a pillow image

        Parameters:
            image_data (bytes): Image data

        Returns:
            PIL.Image: pillow image
        """
        return PIL_Image.open(io.BytesIO(image_data)).convert("RGBA")
