# py-staticmaps
# Copyright (c) 2020 Florian Pigorsch; see /LICENSE for licensing information

import base64
import math
import typing

import svgwrite  # type: ignore

from .color import Color, BLACK, WHITE
from .renderer import Renderer
from .transformer import Transformer

if typing.TYPE_CHECKING:
    # avoid circlic import
    from .object import Object  # pylint: disable=cyclic-import


class SvgRenderer(Renderer):
    """An svg image renderer class that extends a generic renderer class"""

    def __init__(self, transformer: Transformer) -> None:
        Renderer.__init__(self, transformer)
        self._draw = svgwrite.Drawing(
            size=(f"{self._trans.image_width()}px", f"{self._trans.image_height()}px"),
            viewBox=f"0 0 {self._trans.image_width()} {self._trans.image_height()}",
        )
        clip = self._draw.defs.add(self._draw.clipPath(id="page"))
        clip.add(self._draw.rect(insert=(0, 0), size=(self._trans.image_width(), self._trans.image_height())))
        self._group: typing.Optional[svgwrite.container.Group] = None

    def drawing(self) -> svgwrite.Drawing:
        """Return the svg drawing for the image

        :return: svg drawing
        :rtype: svgwrite.Drawing
        """
        return self._draw

    def group(self) -> svgwrite.container.Group:
        """Return the svg group for the image

        :return: svg group
        :rtype: svgwrite.container.Group
        """
        assert self._group is not None
        return self._group

    def render_objects(self, objects: typing.List["Object"]) -> None:
        """Render all objects of static map

        :param objects: objects of static map
        :type objects: typing.List["Object"]
        """
        x_count = math.ceil(self._trans.image_width() / (2 * self._trans.world_width()))
        for obj in objects:
            for p in range(-x_count, x_count + 1):
                self._group = self._draw.g(
                    clip_path="url(#page)", transform=f"translate({p * self._trans.world_width()}, 0)"
                )
                obj.render_svg(self)
                self._draw.add(self._group)
                self._group = None

    def render_background(self, color: typing.Optional[Color]) -> None:
        """Render background of static map

        :param color: background color
        :type color: typing.Optional[Color]
        """
        if color is None:
            return
        group = self._draw.g(clip_path="url(#page)")
        group.add(self._draw.rect(insert=(0, 0), size=self._trans.image_size(), rx=None, ry=None, fill=color.hex_rgb()))
        self._draw.add(group)

    def render_tiles(self, download: typing.Callable[[int, int, int], typing.Optional[bytes]]) -> None:
        """Render background of static map

        :param download: url of tiles provider
        :type download: typing.Callable[[int, int, int], typing.Optional[bytes]]
        """
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

    def render_attribution(self, attribution: typing.Optional[str]) -> None:
        """Render attribution from given tiles provider

        :param attribution: Attribution for the given tiles provider
        :type attribution: typing.Optional[str]:
        """
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
                fill_opacity="0.8",
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
        """Fetch tiles from given tiles provider

        :param download: callable
        :param x: width
        :param y: height
        :type download: typing.Callable[[int, int, int], typing.Optional[bytes]]
        :type x: int
        :type y: int

        :return: svg drawing
        :rtype: typing.Optional[str]
        """
        image_data = download(self._trans.zoom(), x, y)
        if image_data is None:
            return None
        return SvgRenderer.create_inline_image(image_data)

    @staticmethod
    def guess_image_mime_type(data: bytes) -> str:
        """Guess mime type from image data

        :param data: image data
        :type data: bytes
        :return: mime type
        :rtype: str
        """
        if data[:4] == b"\xff\xd8\xff\xe0" and data[6:11] == b"JFIF\0":
            return "image/jpeg"
        if data[1:4] == b"PNG":
            return "image/png"
        return "image/png"

    @staticmethod
    def create_inline_image(image_data: bytes) -> str:
        """Create an svg inline image

        :param image_data: Image data
        :type image_data: bytes

        :return: svg inline image
        :rtype: str
        """
        image_type = SvgRenderer.guess_image_mime_type(image_data)
        return f"data:{image_type};base64,{base64.b64encode(image_data).decode('utf-8')}"
