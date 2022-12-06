"""py-staticmaps - tile_downloader"""
# Copyright (c) 2020 Florian Pigorsch; see /LICENSE for licensing information

import os
import pathlib
import typing

import requests  # type: ignore
import slugify  # type: ignore

from .meta import GITHUB_URL, LIB_NAME, VERSION
from .tile_provider import TileProvider

REQUEST_TIMEOUT = 10


class TileDownloader:
    """A tile downloader class"""

    def __init__(self) -> None:
        self._user_agent = f"Mozilla/5.0+(compatible; {LIB_NAME}/{VERSION}; {GITHUB_URL})"
        self._sanitized_name_cache: typing.Dict[str, str] = {}

    def set_user_agent(self, user_agent: str) -> None:
        """Set the user agent for the downloader

        Parameters:
            user_agent (str): user agent
        """
        self._user_agent = user_agent

    def get(self, provider: TileProvider, cache_dir: str, zoom: int, x: int, y: int) -> typing.Optional[bytes]:
        """Get tiles

        Parameters:
            provider (TileProvider): tile provider
            cache_dir (str): cache directory for tiles
            zoom (int): zoom for static map
            x (int): x value of center for the static map
            y (int): y value of center for the static map

        Returns:
            typing.Optional[bytes]: tiles

        Raises:
            RuntimeError: raises a runtime error if the server response status is not 200
        """
        file_name = None
        if cache_dir is not None:
            file_name = self.cache_file_name(provider, cache_dir, zoom, x, y)
            if os.path.isfile(file_name):
                with open(file_name, "rb") as f:
                    return f.read()

        url = provider.url(zoom, x, y)
        if url is None:
            return None
        res = requests.get(url, headers={"user-agent": self._user_agent}, timeout=REQUEST_TIMEOUT)
        if res.status_code == 200:
            data = res.content
        else:
            raise RuntimeError(f"fetch {url} yields {res.status_code}")

        if file_name is not None:
            pathlib.Path(os.path.dirname(file_name)).mkdir(parents=True, exist_ok=True)
            with open(file_name, "wb") as f:
                f.write(data)
        return data

    def sanitized_name(self, name: str) -> str:
        """Return sanitized name

        Parameters:
            name (str): name to sanitize

        Returns:
            str: sanitized name
        """
        if name in self._sanitized_name_cache:
            return self._sanitized_name_cache[name]
        sanitized = slugify.slugify(name)
        if sanitized is None:
            sanitized = "_"
        self._sanitized_name_cache[name] = sanitized
        return sanitized

    def cache_file_name(self, provider: TileProvider, cache_dir: str, zoom: int, x: int, y: int) -> str:
        """Return a cache file name

        Parameters:
            provider (TileProvider): tile provider
            cache_dir (str): cache directory for tiles
            zoom (int): zoom for static map
            x (int): x value of center for the static map
            y (int): y value of center for the static map

        Returns:
            str: cache file name
        """
        return os.path.join(cache_dir, self.sanitized_name(provider.name()), str(zoom), str(x), f"{y}.png")
