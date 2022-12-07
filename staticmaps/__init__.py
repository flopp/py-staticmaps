"""py-staticmaps __init__"""
# Copyright (c) 2020 Florian Pigorsch; see /LICENSE for licensing information

# flake8: noqa
from .area import Area
from .cairo_renderer import CairoRenderer, cairo_is_supported
from .circle import Circle
from .color import (
    BLACK,
    BLUE,
    BROWN,
    GREEN,
    ORANGE,
    PURPLE,
    RED,
    TRANSPARENT,
    WHITE,
    YELLOW,
    Color,
    parse_color,
    random_color,
)
from .context import Context
from .coordinates import create_latlng, parse_latlng, parse_latlngs, parse_latlngs2rect
from .image_marker import ImageMarker
from .line import Line
from .marker import Marker
from .meta import GITHUB_URL, LIB_NAME, VERSION
from .object import Object, PixelBoundsT
from .pillow_renderer import PillowRenderer
from .svg_renderer import SvgRenderer
from .tile_downloader import TileDownloader
from .tile_provider import (
    TileProvider,
    default_tile_providers,
    tile_provider_ArcGISWorldImagery,
    tile_provider_CartoDarkNoLabels,
    tile_provider_CartoNoLabels,
    tile_provider_None,
    tile_provider_OSM,
    tile_provider_StamenTerrain,
    tile_provider_StamenToner,
    tile_provider_StamenTonerLite,
)
from .transformer import Transformer

__all__ = [
    "Area",
    "CairoRenderer",
    "cairo_is_supported",
    "Circle",
    "BLACK",
    "BLUE",
    "BROWN",
    "GREEN",
    "ORANGE",
    "PURPLE",
    "RED",
    "TRANSPARENT",
    "WHITE",
    "YELLOW",
    "Color",
    "parse_color",
    "random_color",
    "Context",
    "create_latlng",
    "parse_latlng",
    "parse_latlngs",
    "parse_latlngs2rect",
    "ImageMarker",
    "Line",
    "Marker",
    "GITHUB_URL",
    "LIB_NAME",
    "VERSION",
    "Object",
    "PixelBoundsT",
    "PillowRenderer",
    "SvgRenderer",
    "TileDownloader",
    "TileProvider",
    "default_tile_providers",
    "tile_provider_ArcGISWorldImagery",
    "tile_provider_CartoDarkNoLabels",
    "tile_provider_CartoNoLabels",
    "tile_provider_None",
    "tile_provider_OSM",
    "tile_provider_StamenTerrain",
    "tile_provider_StamenToner",
    "tile_provider_StamenTonerLite",
    "Transformer",
]
