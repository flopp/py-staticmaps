#!/usr/bin/env python

import typing

import click

import staticmaps as smm


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
    type=click.Choice(smm.default_tile_providers.keys()),
    default=smm.tile_provider_OSM.name(),
)
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
    file_name: str,
) -> None:
    context = smm.Context()

    context.set_tile_provider(smm.default_tile_providers[tiles])

    if center is not None:
        context.set_center(smm.parse_latlng(center))
    if zoom is not None:
        context.set_zoom(zoom)
    if background is not None:
        context.set_background_color(smm.parse_color(background))
    for coords in line:
        context.add_object(smm.Line(smm.parse_latlngs(coords)))
    for coords in marker:
        context.add_object(smm.Marker(smm.parse_latlng(coords)))

    image = context.render(width, height)
    image.write_to_png(file_name)
    click.echo("wrote result image to {}".format(file_name))


if __name__ == "__main__":
    main()
