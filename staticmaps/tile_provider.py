# py-staticmaps
# Copyright (c) 2020 Florian Pigorsch; see /LICENSE for licensing information

import string
import typing


class TileProvider:
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

    def set_api_key(self, key: str) -> None:
        self._api_key = key

    def name(self) -> str:
        return self._name

    def attribution(self) -> typing.Optional[str]:
        return self._attribution

    @staticmethod
    def tile_size() -> int:
        return 256

    def max_zoom(self) -> int:
        return self._max_zoom

    def url(self, zoom: int, x: int, y: int) -> typing.Optional[str]:
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

tile_provider_ArcGISWorldImagery = TileProvider(
    "arcgis-worldimagery",
    url_pattern="https://server.arcgisonline.com/arcgis/rest/services/World_Imagery/MapServer/tile/$z/$y/$x",
    attribution="Source: Esri, Maxar, GeoEye, Earthstar Geographics, "
    "CNES/Airbus DS, USDA, USGS, AeroGRID, IGN, and the GIS User Community",
    max_zoom=24,
)

default_tile_providers = {
    tile_provider_OSM.name(): tile_provider_OSM,
    tile_provider_StamenTerrain.name(): tile_provider_StamenTerrain,
    tile_provider_StamenToner.name(): tile_provider_StamenToner,
    tile_provider_ArcGISWorldImagery.name(): tile_provider_ArcGISWorldImagery,
}
