"""py-staticmaps - transformer"""
# Copyright (c) 2020 Florian Pigorsch; see /LICENSE for licensing information

import math
import typing

import s2sphere  # type: ignore


# pylint: disable=too-many-instance-attributes
class Transformer:
    """Base class for transforming values"""

    def __init__(self, width: int, height: int, zoom: int, center: s2sphere.LatLng, tile_size: int) -> None:
        self._zoom = zoom
        self._number_of_tiles = 2**zoom
        self._tile_size = tile_size
        self._width = width
        self._height = height

        # Fractional tile index to center of requested area.
        self._tile_center_x, self._tile_center_y = self.ll2t(center)

        ww = width / tile_size
        hh = height / tile_size

        # Top-left tile in requested area
        self._first_tile_x = int(math.floor(self._tile_center_x - ww / 2))
        self._first_tile_y = int(math.floor(self._tile_center_y - hh / 2))

        # Number of tiles (horizontal, vertical) covering requested area
        self._tiles_x = 1 + int(math.floor(self._tile_center_x + ww / 2)) - self._first_tile_x
        self._tiles_y = 1 + int(math.floor(self._tile_center_y + hh / 2)) - self._first_tile_y

        # Pixel-offset of the top-left tile relative to the requested area
        self._tile_offset_x = width / 2 - int((self._tile_center_x - self._first_tile_x) * tile_size)
        self._tile_offset_y = height / 2 - int((self._tile_center_y - self._first_tile_y) * tile_size)

    def world_width(self) -> int:
        """Return the width of the world in pixels depending on tiles provider

        Returns:
            int: width of the world in pixels
        """
        return self._number_of_tiles * self._tile_size

    def image_width(self) -> int:
        """Return the width of the image in pixels

        Returns:
            int: width of the image in pixels
        """
        return self._width

    def image_height(self) -> int:
        """Return the height of the image in pixels

        Returns:
            int: height of the image in pixels
        """
        return self._height

    def zoom(self) -> int:
        """Return the zoom of the static map

        Returns:
            int: zoom of the static map
        """

        return self._zoom

    def image_size(self) -> typing.Tuple[int, int]:
        """Return the size of the image as tuple of width and height

        Returns:
            tuple: width and height of the image in pixels
        """

        return self._width, self._height

    def number_of_tiles(self) -> int:
        """Return number of tiles of static map

        Returns:
            int: number of tiles
        """
        return self._number_of_tiles

    def first_tile_x(self) -> int:
        """Return number of first tile in x

        Returns:
            int: number of first tile
        """
        return self._first_tile_x

    def first_tile_y(self) -> int:
        """Return number of first tile in y

        Returns:
            int: number of first tile
        """
        return self._first_tile_y

    def tiles_x(self) -> int:
        """Return number of tiles in x

        Returns:
            int: number of tiles
        """
        return self._tiles_x

    def tiles_y(self) -> int:
        """Return number of tiles in y

        Returns:
            int: number of tiles
        """
        return self._tiles_y

    def tile_offset_x(self) -> float:
        """Return tile offset in x

        Returns:
            int: tile offset
        """
        return self._tile_offset_x

    def tile_offset_y(self) -> float:
        """Return tile offset in y

        Returns:
            int: tile offset
        """
        return self._tile_offset_y

    def tile_size(self) -> int:
        """Return tile size

        Returns:
            int: tile size
        """
        return self._tile_size

    @staticmethod
    def mercator(latlng: s2sphere.LatLng) -> typing.Tuple[float, float]:
        """Mercator projection

        Parameters:
            latlng (s2sphere.LatLng): LatLng object

        Returns:
            tuple: tile values of given LatLng
        """
        lat = latlng.lat().radians
        lng = latlng.lng().radians
        return lng / (2 * math.pi) + 0.5, (1 - math.log(math.tan(lat) + (1 / math.cos(lat))) / math.pi) / 2

    @staticmethod
    def mercator_inv(x: float, y: float) -> s2sphere.LatLng:
        """Inverse Mercator projection

        Parameters:
            x (float): x value
            y (float): x value

        Returns:
            s2sphere.LatLng: LatLng values of given values
        """
        x = 2 * math.pi * (x - 0.5)
        k = math.exp(4 * math.pi * (0.5 - y))
        y = math.asin((k - 1) / (k + 1))
        return s2sphere.LatLng(y, x)

    def ll2t(self, latlng: s2sphere.LatLng) -> typing.Tuple[float, float]:
        """Transform LatLng values into tiles

        Parameters:
            latlng (s2sphere.LatLng): LatLng object

        Returns:
            tuple: tile values of given LatLng
        """
        x, y = self.mercator(latlng)
        return self._number_of_tiles * x, self._number_of_tiles * y

    def t2ll(self, x: float, y: float) -> s2sphere.LatLng:
        """Transform tile values into LatLng values

        Parameters:
            x (float): x tile
            y (float): x tile

        Returns:
            s2sphere.LatLng: LatLng values of given tile values
        """
        return self.mercator_inv(x / self._number_of_tiles, y / self._number_of_tiles)

    def ll2pixel(self, latlng: s2sphere.LatLng) -> typing.Tuple[float, float]:
        """Transform LatLng values into pixel values

        Parameters:
            latlng (s2sphere.LatLng): LatLng object

        Returns:
            tuple: pixel values of given LatLng
        """
        x, y = self.ll2t(latlng)
        s = self._tile_size
        x = self._width / 2 + (x - self._tile_center_x) * s
        y = self._height / 2 + (y - self._tile_center_y) * s
        return x, y

    def pixel2ll(self, x: float, y: float) -> s2sphere.LatLng:
        """Transform pixel values into LatLng values

        Parameters:
            x (float): x pixel
            y (float): x pixel

        Returns:
            s2sphere.LatLng: LatLng values of given pixel values
        """
        s = self._tile_size
        x = (x - self._width / 2) / s + self._tile_center_x
        y = (y - self._height / 2) / s + self._tile_center_y
        return self.t2ll(x, y)
