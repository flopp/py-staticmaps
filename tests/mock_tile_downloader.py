import io
import cairo
import typing
import staticmaps


class MockTileDownloader(staticmaps.TileDownloader):
    def __init__(self) -> None:
        self._dummy_image_data: typing.Optional[bytes] = None

    def set_user_agent(self, user_agent: str) -> None:
        pass

    def get(
        self, provider: staticmaps.TileProvider, cache_dir: str, zoom: int, x: int, y: int
    ) -> typing.Optional[bytes]:
        if self._dummy_image_data is None:
            surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, provider.tile_size(), provider.tile_size())
            file = io.BytesIO()
            surface.write_to_png(file)
            file.seek(0)
            self._dummy_image_data = file.read()
        return self._dummy_image_data
