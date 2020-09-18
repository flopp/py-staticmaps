# py-staticmaps
# Copyright (c) 2020 Florian Pigorsch; see /LICENSE for licensing information

import typing
import staticmaps


class MockTileDownloader(staticmaps.TileDownloader):
    def __init__(self) -> None:
        super().__init__()
        self._dummy_image_data: typing.Optional[bytes] = None

    def set_user_agent(self, user_agent: str) -> None:
        pass

    def get(
        self, provider: staticmaps.TileProvider, cache_dir: str, zoom: int, x: int, y: int
    ) -> typing.Optional[bytes]:
        return self._dummy_image_data
