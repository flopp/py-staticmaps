# py-staticmaps
# Copyright (c) 2020 Florian Pigorsch; see /LICENSE for licensing information

from abc import ABC, abstractmethod
import typing

from .color import Color
from .transformer import Transformer


if typing.TYPE_CHECKING:
    # avoid circlic import
    from .area import Area  # pylint: disable=cyclic-import
    from .image_marker import ImageMarker  # pylint: disable=cyclic-import
    from .line import Line  # pylint: disable=cyclic-import
    from .marker import Marker  # pylint: disable=cyclic-import
    from .object import Object  # pylint: disable=cyclic-import


class Renderer(ABC):
    """A generic renderer class"""

    def __init__(self, transformer: Transformer) -> None:
        self._trans = transformer

    def transformer(self) -> Transformer:
        """Return transformer object

        :return: transformer
        :rtype: Transformer
        """
        return self._trans

    @abstractmethod
    def render_objects(self, objects: typing.List["Object"]) -> None:
        """Render all objects of static map

        :param objects: objects of static map
        :type objects: typing.List["Object"]
        """

    @abstractmethod
    def render_background(self, color: typing.Optional[Color]) -> None:
        """Render background of static map

        :param color: background color
        :type color: typing.Optional[Color]
        """

    @abstractmethod
    def render_tiles(self, download: typing.Callable[[int, int, int], typing.Optional[bytes]]) -> None:
        """Render background of static map

        :param download: url of tiles provider
        :type download: typing.Callable[[int, int, int], typing.Optional[bytes]]
        """

    def render_marker_object(self, marker: "Marker") -> None:
        """Render marker object of static map

        :param marker: marker object
        :type marker: Marker
        """

    def render_image_marker_object(self, marker: "ImageMarker") -> None:
        """Render image marker object of static map

        :param marker: image marker object
        :type marker: ImageMarker
        """

    def render_line_object(self, line: "Line") -> None:
        """Render line object of static map

        :param line: line object
        :type line: Line
        """

    def render_area_object(self, area: "Area") -> None:
        """Render area object of static map

        :param area: area object
        :type area: Area
        """

    @abstractmethod
    def render_attribution(self, attribution: typing.Optional[str]) -> None:
        """Render attribution from given tiles provider

        :param attribution: Attribution for the given tiles provider
        :type attribution: typing.Optional[str]:
        """
