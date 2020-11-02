# py-staticmaps
# Copyright (c) 2020 Florian Pigorsch; see /LICENSE for licensing information

# flake8: noqa
from .area import Area
from .circle import Circle
from .color import (
    parse_color,
    random_color,
    Color,
    BLACK,
    BLUE,
    BROWN,
    GREEN,
    ORANGE,
    PURPLE,
    RED,
    YELLOW,
    WHITE,
    TRANSPARENT,
)
from .context import Context
from .coordinates import create_latlng, parse_latlng, parse_latlngs
from .line import Line
from .marker import Marker
from .meta import GITHUB_URL, LIB_NAME, VERSION
from .object import Object, PixelBoundsT
from .tile_downloader import TileDownloader
from .tile_provider import (
    TileProvider,
    default_tile_providers,
    tile_provider_OSM,
    tile_provider_StamenTerrain,
    tile_provider_StamenToner,
    tile_provider_ArcGISWorldImagery,
)
from .transformer import Transformer
