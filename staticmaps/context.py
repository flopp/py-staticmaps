import base64
import math
import os
import typing

import appdirs  # type: ignore
import s2sphere  # type: ignore
import svgwrite  # type: ignore

from .tile_downloader import TileDownloader
from .tile_provider import TileProvider, tile_provider_OSM
from .transformer import Transformer
from .object import Object, PixelBoundsT
from .color import Color, BLACK, WHITE


class Context:
    def __init__(self) -> None:
        self._background_color: typing.Optional[Color] = None
        self._objects: typing.List[Object] = []
        self._center: typing.Optional[s2sphere.LatLng] = None
        self._zoom: typing.Optional[int] = None
        self._tile_provider = tile_provider_OSM
        self._tile_downloader = TileDownloader()
        self._cache_dir = os.path.join(appdirs.user_cache_dir("py-staticmaps"), "tiles")

    def set_zoom(self, zoom: int) -> None:
        if zoom < 0 or zoom > 30:
            raise ValueError("Bad zoom value: {}".format(zoom))
        self._zoom = zoom

    def set_center(self, latlng: s2sphere.LatLng) -> None:
        self._center = latlng

    def set_background_color(self, color: Color) -> None:
        self._background_color = color

    def set_cache_dir(self, directory: str) -> None:
        self._cache_dir = directory

    def set_tile_downloader(self, downloader: TileDownloader) -> None:
        self._tile_downloader = downloader

    def set_tile_provider(self, provider: TileProvider) -> None:
        self._tile_provider = provider

    @staticmethod
    def guess_image_mime_type(data: bytes) -> str:
        if data[:4] == b"\xff\xd8\xff\xe0" and data[6:11] == b"JFIF\0":
            return "image/jpeg"
        if data[1:4] == b"PNG":
            return "image/png"
        return "image/png"

    def fetch_tile_image(self, z: int, x: int, y: int) -> typing.Optional[str]:
        image_data = self._tile_downloader.get(self._tile_provider, self._cache_dir, z, x, y)
        if image_data is None:
            return None
        image_type = self.guess_image_mime_type(image_data)
        return f"data:{image_type};base64,{base64.b64encode(image_data).decode('utf-8')}"

    def render(self, width: int, height: int) -> svgwrite.Drawing:
        center, zoom = self.determine_center_zoom(width, height)
        if center is None or zoom is None:
            raise RuntimeError("Cannot render map without center/zoom.")

        draw = svgwrite.Drawing(size=(f"{width}px", f"{height}px"), viewBox=f"0 0 {width} {height}")
        clip = draw.defs.add(draw.clipPath(id="page"))
        clip.add(draw.rect(insert=(0, 0), size=(width, height)))
        trans = Transformer(width, height, zoom, center, self._tile_provider.tile_size())

        self.render_background(draw, trans)
        self.render_tiles(draw, trans)
        self.render_objects(draw, trans)
        self.render_attribution(draw, trans)

        return draw
        
    def add_object(self, obj: Object) -> None:
        self._objects.append(obj)

    def object_bounds(self) -> typing.Optional[s2sphere.LatLngRect]:
        if len(self._objects) == 0:
            return None
        bounds = s2sphere.LatLngRect()
        for obj in self._objects:
            bounds = bounds.union(obj.bounds())
        return bounds

    def extra_pixel_bounds(self) -> PixelBoundsT:
        max_l, max_t, max_r, max_b = 0, 0, 0, 0
        attribution = self._tile_provider.attribution()
        if (attribution is None) or (attribution == ""):
            max_b = 12
        for obj in self._objects:
            (l, t, r, b) = obj.extra_pixel_bounds()
            max_l = max(max_l, l)
            max_t = max(max_t, t)
            max_r = max(max_r, r)
            max_b = max(max_b, b)
        return (max_l, max_t, max_r, max_b)

    def render_background(self, draw: svgwrite.Drawing, trans: Transformer) -> None:
        if self._background_color is None:
            return
        group = draw.g(clip_path="url(#page)")
        group.add(
            draw.rect(
                insert=(0, 0), size=trans.image_size(), rx=None, ry=None, fill=self._background_color.hex_string()
            )
        )
        draw.add(group)

    def render_tiles(self, draw: svgwrite.Drawing,trans: Transformer) -> None:
        group = draw.g(clip_path="url(#page)")
        for yy in range(0, trans.tiles_y()):
            y = trans.first_tile_y() + yy
            if y < 0 or y >= trans.number_of_tiles():
                continue
            for xx in range(0, trans.tiles_x()):
                x = (trans.first_tile_x() + xx) % trans.number_of_tiles()
                try:
                    tile_img = self.fetch_tile_image(trans.zoom(), x, y)
                    if tile_img is None:
                        continue
                    group.add(
                        draw.image(
                            tile_img,
                            insert=(
                                xx * self._tile_provider.tile_size() + trans.tile_offset_x(),
                                yy * self._tile_provider.tile_size() + trans.tile_offset_y(),
                            ),
                            size=(self._tile_provider.tile_size(), self._tile_provider.tile_size()),
                        )
                    )
                except RuntimeError:
                    pass
        draw.add(group)

    def render_objects(self, draw: svgwrite.Drawing, trans: Transformer) -> None:
        group = draw.g(clip_path="url(#page)")
        for obj in self._objects:
            obj.render(trans, draw, group)
        draw.add(group)

    def render_attribution(self, draw: svgwrite.Drawing, trans: Transformer) -> None:
        attribution = self._tile_provider.attribution()
        if (attribution is None) or (attribution == ""):
            return
        group = draw.g(clip_path="url(#page)")
        group.add(
            draw.rect(
                insert=(0, trans.image_height() - 12),
                size=(trans.image_width(), 12),
                rx=None,
                ry=None,
                fill=WHITE.hex_string(),
                fill_opacity="0.4",
            )
        )
        group.add(
            draw.text(
                attribution,
                insert=(2, trans.image_height() - 3),
                font_family="Arial, Helvetica, sans-serif",
                font_size="9px",
                fill=BLACK.hex_string(),
            )
        )
        draw.add(group)

    def determine_center_zoom(self, width: int, height: int) -> typing.Tuple[s2sphere.LatLng, typing.Optional[int]]:
        if self._center is not None:
            if self._zoom is not None:
                return self._center, self.clamp_zoom(self._zoom)
        b = self.object_bounds()
        if b is None:
            return self._center, self.clamp_zoom(self._zoom)
        if self._zoom is not None:
            return b.get_center(), self.clamp_zoom(self._zoom)
        if self._center is not None:
            b = b.union(s2sphere.LatLngRect(self._center, self._center))
        if b.is_point():
            return b.get_center(), None
        pixel_margin = self.extra_pixel_bounds()
        w = (width - 2.0 * max(pixel_margin[0], pixel_margin[2])) / self._tile_provider.tile_size()
        h = (height - 2.0 * max(pixel_margin[1], pixel_margin[3])) / self._tile_provider.tile_size()
        min_y = (1.0 - math.log(math.tan(b.lat_lo().radians) + (1.0 / math.cos(b.lat_lo().radians))) / math.pi) / 2.0
        max_y = (1.0 - math.log(math.tan(b.lat_hi().radians) + (1.0 / math.cos(b.lat_hi().radians))) / math.pi) / 2.0
        dx = (b.lng_hi().degrees - b.lng_lo().degrees) / 360.0
        if dx < 0:
            dx += math.ceil(math.fabs(dx))
        if dx > 1:
            dx -= math.floor(dx)
        dy = math.fabs(max_y - min_y)
        for zoom in range(1, self._tile_provider.max_zoom()):
            tiles = 2 ** zoom
            if (dx * tiles > w) or (dy * tiles > h):
                return b.get_center(), zoom - 1
        return b.get_center(), self._tile_provider.max_zoom()

    def clamp_zoom(self, zoom: typing.Optional[int]) -> typing.Optional[int]:
        if zoom is None:
            return None
        if zoom < 0:
            return 0
        if zoom > self._tile_provider.max_zoom():
            return self._tile_provider.max_zoom()
        return zoom
