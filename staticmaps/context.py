import appdirs  # type: ignore
import cairo
import io
import math
import os
from PIL import Image  # type: ignore
import s2sphere as s2  # type: ignore
import typing
from .tile_downloader import TileDownloader
from .tile_provider import TileProvider, tile_provider_OSM
from .transformer import Transformer
from .object import Object
from .color import ColorT


class Context:
    def __init__(self) -> None:
        self._background_color: typing.Optional[ColorT] = None
        self._objects: typing.List[Object] = []
        self._center: typing.Optional[s2.LatLng] = None
        self._zoom: typing.Optional[int] = None
        self._tile_provider = tile_provider_OSM
        self._tile_downloader = TileDownloader()
        self._cache_dir = os.path.join(appdirs.user_cache_dir("staticmaps"), "tiles")

    def set_zoom(self, zoom: int) -> None:
        if zoom < 0 or zoom > 30:
            raise ValueError("Bad zoom value: {}".format(zoom))
        self._zoom = zoom

    def set_center(self, latlng: s2.LatLng) -> None:
        self._center = latlng

    def set_background_color(self, color: ColorT) -> None:
        self._background_color = color

    def set_cache_dir(self, dir: str) -> None:
        self._cache_dir = dir

    def set_tile_downloader(self, downloader: TileDownloader) -> None:
        self._tile_downloader = downloader

    def set_tile_provider(self, provider: TileProvider) -> None:
        self._tile_provider = provider

    def fetch_tile_image(self, z: int, x: int, y: int) -> typing.Optional[cairo.ImageSurface]:
        image_data = self._tile_downloader.get(self._tile_provider, self._cache_dir, z, x, y)
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

    def render(self, width: int, height: int) -> cairo.ImageSurface:
        center, zoom = self.determine_center_zoom(width, height)
        if center is None or zoom is None:
            raise RuntimeError("Cannot render map without center/zoom.")

        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
        cairo_context = cairo.Context(surface)
        if self._background_color is not None:
            cairo_context.set_source_rgba(*self._background_color)
            cairo_context.rectangle(0, 0, width, height)
            cairo_context.fill()
        trans = Transformer(width, height, zoom, center, self._tile_provider.tile_size())

        # render tiles
        tiles = 2 ** zoom
        for yy in range(0, trans.tiles_y()):
            y = trans.first_tile_y() + yy
            if y < 0 or y >= tiles:
                continue
            for xx in range(0, trans.tiles_x()):
                x = (trans.first_tile_x() + xx) % tiles
                try:
                    tile_img = self.fetch_tile_image(zoom, x, y)
                    if tile_img is None:
                        continue
                    cairo_context.save()
                    cairo_context.translate(
                        xx * self._tile_provider.tile_size() + trans.tile_offset_x(),
                        yy * self._tile_provider.tile_size() + trans.tile_offset_y(),
                    )
                    cairo_context.set_source_surface(tile_img)
                    cairo_context.paint()
                    cairo_context.restore()
                except RuntimeError:
                    pass

        # render objects
        for object in self._objects:
            object.render(trans, cairo_context)

        self.render_attribution(cairo_context, width, height)

        return surface

    def add_object(self, object: Object) -> None:
        self._objects.append(object)

    def object_bounds(self) -> typing.Optional[s2.LatLngRect]:
        if len(self._objects) == 0:
            return None
        bounds = s2.LatLngRect()
        for obj in self._objects:
            bounds = bounds.union(obj.bounds())
        return bounds

    def render_attribution(self, cairo_context: cairo.Context, width: int, height: int) -> None:
        attribution = self._tile_provider.attribution()
        if (attribution is None) or (attribution == ""):
            return
        cairo_context.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        font_size = 12
        while True:
            cairo_context.set_font_size(font_size)
            (f_ascent, f_descent, f_height, f_max_x_adv, f_max_y_adv,) = cairo_context.font_extents()
            (t_x_bearing, t_y_bearing, t_width, t_height, t_x_advance, t_y_advance,) = cairo_context.text_extents(
                attribution
            )
            if t_width < width - 4:
                break
            font_size = font_size - 0.25
        cairo_context.set_source_rgba(0, 0, 0, 0.5)
        cairo_context.rectangle(0, height - f_height - f_descent - 2, width, height)
        cairo_context.fill()

        cairo_context.set_source_rgba(1, 1, 1, 1)
        cairo_context.move_to(width - t_width - 4, height - f_descent - 2)
        cairo_context.show_text(attribution)
        cairo_context.stroke()

    def determine_center_zoom(self, width: int, height: int) -> typing.Tuple[s2.LatLng, typing.Optional[int]]:
        if self._center is not None:
            if self._zoom is not None:
                return self._center, self.clamp_zoom(self._zoom)
        b = self.object_bounds()
        if b is None:
            return self._center, self.clamp_zoom(self._zoom)
        if self._zoom is not None:
            return b.get_center(), self.clamp_zoom(self._zoom)
        if self._center is not None:
            b = b.union(s2.LatLngRect(self._center, self._center))
        if b.is_point():
            return b.get_center(), None
        tile_size = self._tile_provider.tile_size()
        # TODO: + extra margin pixels
        margin = 4
        w = (width - 2.0 * margin) / tile_size
        h = (height - 2.0 * margin) / tile_size
        minX = (b.lng_lo().degrees + 180.0) / 360.0
        maxX = (b.lng_hi().degrees + 180.0) / 360.0
        minY = (1.0 - math.log(math.tan(b.lat_lo().radians) + (1.0 / math.cos(b.lat_lo().radians))) / math.pi) / 2.0
        maxY = (1.0 - math.log(math.tan(b.lat_hi().radians) + (1.0 / math.cos(b.lat_hi().radians))) / math.pi) / 2.0
        dx = maxX - minX
        if dx < 0:
            dx += math.ceil(math.fabs(dx))
        if dx > 1:
            dx -= math.floor(dx)
        dy = math.fabs(maxY - minY)
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
