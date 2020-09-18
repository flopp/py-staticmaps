# py-staticmaps
# Copyright (c) 2020 Florian Pigorsch; see /LICENSE for licensing information

import os
import pathlib
import typing

import requests
import slugify  # type: ignore

from .meta import GITHUB_URL, LIB_NAME, VERSION
from .tile_provider import TileProvider


class TileDownloader:
    def __init__(self) -> None:
        self._user_agent = f"Mozilla/5.0+(compatible; {LIB_NAME}/{VERSION}; {GITHUB_URL})"
        self._sanitized_name_cache: typing.Dict[str, str] = {}

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

    def sanitized_name(self, name: str) -> str:
        if name in self._sanitized_name_cache:
            return self._sanitized_name_cache[name]
        sanitized = slugify.slugify(name)
        if sanitized is None:
            sanitized = "_"
        self._sanitized_name_cache[name] = sanitized
        return sanitized

    def cache_file_name(self, provider: TileProvider, cache_dir: str, zoom: int, x: int, y: int) -> str:
        return os.path.join(cache_dir, self.sanitized_name(provider.name()), str(zoom), str(x), "{}.png".format(y))
