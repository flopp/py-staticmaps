import math
import s2sphere as s2  # type: ignore
import typing


class Transformer:
    def __init__(self, width: int, height: int, zoom: int, center: s2.LatLng, tile_size: int) -> None:
        self._num_tiles = 2 ** zoom
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
        return self._num_tiles * self._tile_size

    def image_width(self) -> int:
        return self._width

    def first_tile_x(self) -> int:
        return self._first_tile_x

    def first_tile_y(self) -> int:
        return self._first_tile_y

    def tiles_x(self) -> int:
        return self._tiles_x

    def tiles_y(self) -> int:
        return self._tiles_y

    def tile_offset_x(self) -> float:
        return self._tile_offset_x

    def tile_offset_y(self) -> float:
        return self._tile_offset_y

    def ll2t(self, latlng: s2.LatLng) -> typing.Tuple[float, float]:
        lat = latlng.lat().radians
        lng = latlng.lng().radians
        x = (lng + math.pi) / (2 * math.pi)
        y = (1 - math.log(math.tan(lat) + (1 / math.cos(lat))) / math.pi) / 2
        return self._num_tiles * x, self._num_tiles * y

    def ll2pixel(self, latlng: s2.LatLng) -> typing.Tuple[float, float]:
        x, y = self.ll2t(latlng)
        s = self._tile_size
        x = self._width / 2 + (x - self._tile_center_x) * s
        y = self._height / 2 + (y - self._tile_center_y) * s
        return x, y
