#!/usr/bin/env python

# py-staticmaps
# Copyright (c) 2020 Florian Pigorsch; see /LICENSE for licensing information

import os
import typing

import click

import staticmaps


@click.command()
@click.option("--center", type=str, default=None)
@click.option("--zoom", type=int, default=None)
@click.option("--width", type=int, required=True)
@click.option("--height", type=int, required=True)
@click.option("--background", type=str, default=None)
@click.option("--marker", type=str, multiple=True)
@click.option("--line", type=str, multiple=True)
@click.option(
    "--tiles",
    type=click.Choice(staticmaps.default_tile_providers.keys()),
    default=staticmaps.tile_provider_OSM.name(),
)
@click.option("--file_format", type=click.Choice(["png", "svg", "guess"]), default="guess")
@click.argument("file_name", type=str, required=True)
def main(
    center: typing.Optional[str],
    zoom: typing.Optional[int],
    width: int,
    height: int,
    background: typing.Optional[str],
    marker: typing.List[str],
    line: typing.List[str],
    tiles: str,
    file_format: str,
    file_name: str,
) -> None:
    context = staticmaps.Context()

    context.set_tile_provider(staticmaps.default_tile_providers[tiles])

    if center is not None:
        context.set_center(staticmaps.parse_latlng(center))
    if zoom is not None:
        context.set_zoom(zoom)
    if background is not None:
        context.set_background_color(staticmaps.parse_color(background))
    for coords in line:
        context.add_object(staticmaps.Line(staticmaps.parse_latlngs(coords)))
    for coords in marker:
        context.add_object(staticmaps.Marker(staticmaps.parse_latlng(coords)))

    if file_format == "guess":
        file_format = guess_file_format(file_name)
    if file_format == "png":
        image = context.render_cairo(width, height)
        image.write_to_png(file_name)
    else:
        svg_image = context.render_svg(width, height)
        with open(file_name, "w", encoding="utf-8") as f:
            svg_image.write(f, pretty=True)
    click.echo("wrote result image to {}".format(file_name))


def guess_file_format(file_name: str) -> str:
    extension = os.path.splitext(file_name)[1]
    if extension == ".png":
        return "png"
    if extension == ".svg":
        return "svg"
    raise RuntimeError("Cannot guess the image type from the given file name: {file_name}")


if __name__ == "__main__":
    main()
