import os
import pathlib
import typing

import requests

from .tile_provider import TileProvider
from .version import __version__


class TileDownloader:
    def __init__(self) -> None:
        self._user_agent = f"Mozilla/5.0+(compatible; staticmaps/{__version__}; https://github.com/flopp/py-staticmaps)"

    def set_user_agent(self, user_agent: str) -> None:
        self._user_agent = user_agent

    def get(self, provider: TileProvider, cache_dir: str, zoom: int, x: int, y: int) -> typing.Optional[bytes]:
        file_name = None
        if cache_dir is not None:
            file_name = self.cache_file_name(provider, cache_dir, zoom, x, y)
            if os.path.isfile(file_name):
                with open(file_name, "rb") as f:
                    return f.read()

        url = provider.url(zoom, x, y)
        if url is None:
            return None
        res = requests.get(url, headers={"user-agent": self._user_agent})
        if res.status_code == 200:
            data = res.content
        else:
            raise RuntimeError("fetch {} yields {}".format(url, res.status_code))

        if file_name is not None:
            pathlib.Path(os.path.dirname(file_name)).mkdir(parents=True, exist_ok=True)
            with open(file_name, "wb") as f:
                f.write(data)
        return data

    @staticmethod
    def cache_file_name(provider: TileProvider, cache_dir: str, zoom: int, x: int, y: int) -> str:
        return os.path.join(cache_dir, provider.name(), str(zoom), str(x), "{}.png".format(y))
