"""py-staticmaps - tile_provider"""
# Copyright (c) 2020 Florian Pigorsch; see /LICENSE for licensing information

import string
import typing


class TileProvider:
    """A tile provider class with several pre-defined tile providers"""

    def __init__(
        self,
        name: str,
        url_pattern: str,
        shards: typing.Optional[typing.List[str]] = None,
        api_key: typing.Optional[str] = None,
        attribution: typing.Optional[str] = None,
        max_zoom: int = 24,
    ) -> None:
        self._name = name
        self._url_pattern = string.Template(url_pattern)
        self._shards = shards
        self._api_key = api_key
        self._attribution = attribution
        self._max_zoom = max_zoom if ((max_zoom is not None) and (max_zoom <= 20)) else 20

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TileProvider):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return (
            self._name == other._name
            and str(self._url_pattern) == str(other._url_pattern)
            and self._shards == other._shards
            and self._api_key == other._api_key
            and self._attribution == other._attribution
            and self._max_zoom == other._max_zoom
        )

    def set_api_key(self, key: str) -> None:
        """Set an api key

        Parameters:
            key (str): api key
        """
        self._api_key = key

    def name(self) -> str:
        """Return the name of the tile provider

        Returns:
            str: name of tile provider
        """
        return self._name

    def attribution(self) -> typing.Optional[str]:
        """Return the attribution of the tile provider

        Returns:
            typing.Optional[str]: attribution of tile provider if
            available
        """
        return self._attribution

    @staticmethod
    def tile_size() -> int:
        """Return the tile size

        Returns:
            int: tile size
        """
        return 256

    def max_zoom(self) -> int:
        """Return the maximum zoom of the tile provider

        Returns:
            int: maximum zoom
        """
        return self._max_zoom

    def url(self, zoom: int, x: int, y: int) -> typing.Optional[str]:
        """Return the url of the tile provider

        Parameters:
            zoom (int): zoom for static map
            x (int): x value of center for the static map
            y (int): y value of center for the static map

        Returns:
            typing.Optional[str]: url with zoom, x and y values
        """
        if len(self._url_pattern.template) == 0:
            return None
        if (zoom < 0) or (zoom > self._max_zoom):
            return None
        shard = None
        if self._shards is not None and len(self._shards) > 0:
            shard = self._shards[(x + y) % len(self._shards)]
        return self._url_pattern.substitute(s=shard, z=zoom, x=x, y=y, k=self._api_key)


tile_provider_OSM = TileProvider(
    "osm",
    url_pattern="https://$s.tile.openstreetmap.org/$z/$x/$y.png",
    shards=["a", "b", "c"],
    attribution="Maps & Data (C) OpenStreetMap.org contributors",
    max_zoom=19,
)

tile_provider_StamenTerrain = TileProvider(
    "stamen-terrain",
    url_pattern="http://$s.tile.stamen.com/terrain/$z/$x/$y.png",
    shards=["a", "b", "c", "d"],
    attribution="Maps (C) Stamen, Data (C) OpenStreetMap.org contributors",
    max_zoom=18,
)

tile_provider_StamenToner = TileProvider(
    "stamen-toner",
    url_pattern="http://$s.tile.stamen.com/toner/$z/$x/$y.png",
    shards=["a", "b", "c", "d"],
    attribution="Maps (C) Stamen, Data (C) OpenStreetMap.org contributors",
    max_zoom=20,
)

tile_provider_StamenTonerLite = TileProvider(
    "stamen-toner-lite",
    url_pattern="http://$s.tile.stamen.com/toner-lite/$z/$x/$y.png",
    shards=["a", "b", "c", "d"],
    attribution="Maps (C) Stamen, Data (C) OpenStreetMap.org contributors",
    max_zoom=20,
)

tile_provider_ArcGISWorldImagery = TileProvider(
    "arcgis-worldimagery",
    url_pattern="https://server.arcgisonline.com/arcgis/rest/services/World_Imagery/MapServer/tile/$z/$y/$x",
    attribution="Source: Esri, Maxar, GeoEye, Earthstar Geographics, "
    "CNES/Airbus DS, USDA, USGS, AeroGRID, IGN, and the GIS User Community",
    max_zoom=24,
)

tile_provider_Carto = TileProvider(
    "carto",
    url_pattern="http://$s.basemaps.cartocdn.com/rastertiles/light_all/$z/$x/$y.png",
    shards=["a", "b", "c", "d"],
    attribution="Maps (C) CARTO (C) OpenStreetMap.org contributors",
    max_zoom=20,
)

tile_provider_CartoNoLabels = TileProvider(
    "carto-nolabels",
    url_pattern="http://$s.basemaps.cartocdn.com/rastertiles/light_nolabels/$z/$x/$y.png",
    shards=["a", "b", "c", "d"],
    attribution="Maps (C) CARTO (C) OpenStreetMap.org contributors",
    max_zoom=20,
)

tile_provider_CartoDark = TileProvider(
    "carto-dark",
    url_pattern="http://$s.basemaps.cartocdn.com/rastertiles/dark_all/$z/$x/$y.png",
    shards=["a", "b", "c", "d"],
    attribution="Maps (C) CARTO (C) OpenStreetMap.org contributors",
    max_zoom=20,
)

tile_provider_CartoDarkNoLabels = TileProvider(
    "carto-darknolabels",
    url_pattern="http://$s.basemaps.cartocdn.com/rastertiles/dark_nolabels/$z/$x/$y.png",
    shards=["a", "b", "c", "d"],
    attribution="Maps (C) CARTO (C) OpenStreetMap.org contributors",
    max_zoom=20,
)

tile_provider_StadiaAlidadeSmooth = TileProvider(
    "stadia-alidade-smooth",
    url_pattern="https://tiles.stadiamaps.com/tiles/alidade_smooth/$z/$x/$y.png?api_key=$k",
    shards=["a", "b", "c", "d"],
    attribution="Maps (C) Stadia Maps (C) OpenMapTiles (C) OpenStreetMap.org contributors",
    max_zoom=20,
    api_key="",
)

tile_provider_StadiaAlidadeSmoothDark = TileProvider(
    "stadia-alidade-smooth",
    url_pattern="https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/$z/$x/$y.png?api_key=$k",
    shards=["a", "b", "c", "d"],
    attribution="Maps (C) Stadia Maps (C) OpenMapTiles (C) OpenStreetMap.org contributors",
    max_zoom=20,
)

tile_provider_JawgLight = TileProvider(
    "jawg-light",
    url_pattern="https://$s.tile.jawg.io/jawg-light/$z/$x/$y.png?access-token=$k",
    shards=["a", "b", "c", "d"],
    attribution="Maps (C) Jawg Maps (C) OpenStreetMap.org contributors",
    max_zoom=22,
)

tile_provider_JawgDark = TileProvider(
    "jawg-dark",
    url_pattern="https://$s.tile.jawg.io/jawg-dark/$z/$x/$y.png?access-token=$k",
    shards=["a", "b", "c", "d"],
    attribution="Maps (C) Jawg Maps (C) OpenStreetMap.org contributors",
    max_zoom=22,
)

tile_provider_None = TileProvider(
    "none",
    url_pattern="",
    attribution=None,
    max_zoom=99,
)

default_tile_providers = {
    tile_provider_OSM.name(): tile_provider_OSM,
    tile_provider_StamenTerrain.name(): tile_provider_StamenTerrain,
    tile_provider_StamenToner.name(): tile_provider_StamenToner,
    tile_provider_StamenTonerLite.name(): tile_provider_StamenTonerLite,
    tile_provider_ArcGISWorldImagery.name(): tile_provider_ArcGISWorldImagery,
    tile_provider_Carto.name(): tile_provider_Carto,
    tile_provider_CartoNoLabels.name(): tile_provider_CartoNoLabels,
    tile_provider_CartoDark.name(): tile_provider_CartoDark,
    tile_provider_CartoDarkNoLabels.name(): tile_provider_CartoDarkNoLabels,
    tile_provider_StadiaAlidadeSmooth.name(): tile_provider_StadiaAlidadeSmooth,
    tile_provider_StadiaAlidadeSmoothDark.name(): tile_provider_StadiaAlidadeSmoothDark,
    tile_provider_JawgLight.name(): tile_provider_JawgLight,
    tile_provider_JawgDark.name(): tile_provider_JawgDark,
    tile_provider_None.name(): tile_provider_None,
}
