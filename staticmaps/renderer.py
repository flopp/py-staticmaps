"""py-staticmaps - renderer"""
# Copyright (c) 2020 Florian Pigorsch; see /LICENSE for licensing information

import typing
from abc import ABC, abstractmethod

import s2sphere  # type: ignore

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

        Returns:
            Transformer: transformer
        """
        return self._trans

    @abstractmethod
    def render_objects(
        self,
        objects: typing.List["Object"],
        bbox: s2sphere.LatLngRect,
        epb: typing.Optional[typing.Tuple[int, int, int, int]] = None,
    ) -> None:
        """Render all objects of static map

        Parameters:
            objects (typing.List["Object"]): objects of static map
            bbox (s2sphere.LatLngRect): boundary box of all objects
            epb (typing.Tuple[int, int, int, int]): extra pixel bounds
        """

    @abstractmethod
    def render_background(self, color: typing.Optional[Color]) -> None:
        """Render background of static map

        Parameters:
            color (typing.Optional[Color]): background color
        """

    @abstractmethod
    def render_tiles(
        self,
        download: typing.Callable[[int, int, int], typing.Optional[bytes]],
        bbox: s2sphere.LatLngRect,
        epb: typing.Optional[typing.Tuple[int, int, int, int]] = None,
    ) -> None:
        """Render tiles of static map

        Parameters:
            download (typing.Callable[[int, int, int], typing.Optional[bytes]]): url of tiles provider
            bbox (s2sphere.LatLngRect): boundary box of all objects
            epb (typing.Tuple[int, int, int, int]): extra pixel bounds
        """

    def render_marker_object(self, marker: "Marker") -> None:
        """Render marker object of static map

        Parameters:
            marker (Marker): marker object
        """

    def render_image_marker_object(self, marker: "ImageMarker") -> None:
        """Render image marker object of static map

        Parameters:
            marker (ImageMarker): image marker object
        """

    def render_line_object(self, line: "Line") -> None:
        """Render line object of static map

        Parameters:
            line (Line): line object
        """

    def render_area_object(self, area: "Area") -> None:
        """Render area object of static map

        Parameters:
            area (Area): area object
        """

    @abstractmethod
    def render_attribution(self, attribution: typing.Optional[str]) -> None:
        """Render attribution from given tiles provider

        Parameters:
            attribution (typing.Optional[str]:): Attribution for the
                given tiles provider
        """
