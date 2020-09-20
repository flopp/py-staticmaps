#!/usr/bin/env python

# py-staticmaps
# Copyright (c) 2020 Florian Pigorsch; see /LICENSE for licensing information

import argparse
import os

import staticmaps


def main() -> None:
    args_parser = argparse.ArgumentParser(prog="createstaticmap")
    args_parser.add_argument(
        "--center",
        metavar="LAT,LNG",
        type=str,
    )
    args_parser.add_argument(
        "--zoom",
        metavar="ZOOM",
        type=int,
    )
    args_parser.add_argument(
        "--width",
        metavar="WIDTH",
        type=int,
        required=True,
    )
    args_parser.add_argument(
        "--height",
        metavar="HEIGHT",
        type=int,
        required=True,
    )
    args_parser.add_argument(
        "--background",
        metavar="COLOR",
        type=str,
    )
    args_parser.add_argument(
        "--marker",
        metavar="LAT,LNG",
        type=str,
        action="append",
    )
    args_parser.add_argument(
        "--line",
        metavar="LAT,LNG LAT,LNG ...",
        type=str,
        action="append",
    )
    args_parser.add_argument(
        "--area",
        metavar="LAT,LNG LAT,LNG ...",
        type=str,
        action="append",
    )
    args_parser.add_argument(
        "--tiles",
        metavar="TILEPROVIDER",
        type=str,
        choices=staticmaps.default_tile_providers.keys(),
        default=staticmaps.tile_provider_OSM.name(),
    )
    args_parser.add_argument(
        "--file-format",
        metavar="FORMAT",
        type=str,
        choices=["png", "svg", "guess"],
        default="guess",
    )
    args_parser.add_argument(
        "filename",
        metavar="FILE",
        type=str,
        nargs=1,
    )

    args = args_parser.parse_args()

    context = staticmaps.Context()

    context.set_tile_provider(staticmaps.default_tile_providers[args.tiles])

    if args.center is not None:
        context.set_center(staticmaps.parse_latlng(args.center))
    if args.zoom is not None:
        context.set_zoom(args.zoom)
    if args.background is not None:
        context.set_background_color(staticmaps.parse_color(args.background))
    if args.area:
        for coords in args.area:
            context.add_object(staticmaps.Area(staticmaps.parse_latlngs(coords)))
    if args.line:
        for coords in args.line:
            context.add_object(staticmaps.Line(staticmaps.parse_latlngs(coords)))
    if args.marker:
        for coords in args.marker:
            context.add_object(staticmaps.Marker(staticmaps.parse_latlng(coords)))

    file_name = args.filename[0]
    if determine_file_format(args.file_format, file_name) == "png":
        image = context.render_cairo(args.width, args.height)
        image.write_to_png(file_name)
    else:
        svg_image = context.render_svg(args.width, args.height)
        with open(file_name, "w", encoding="utf-8") as f:
            svg_image.write(f, pretty=True)
    print(f"wrote result image to {file_name}")


def determine_file_format(file_format: str, file_name: str) -> str:
    if file_format != "guess":
        return file_format
    extension = os.path.splitext(file_name)[1]
    if extension == ".png":
        return "png"
    if extension == ".svg":
        return "svg"
    raise RuntimeError("Cannot guess the image type from the given file name: {file_name}")


if __name__ == "__main__":
    main()
