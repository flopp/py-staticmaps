#!/usr/bin/env python

"""py-staticmaps - Example Tile Providers"""
# Copyright (c) 2020 Florian Pigorsch; see /LICENSE for licensing information

import staticmaps

context = staticmaps.Context()

p1 = staticmaps.create_latlng(48.005774, 7.834042)
p2 = staticmaps.create_latlng(47.988716, 7.868804)
p3 = staticmaps.create_latlng(47.985958, 7.824601)

context.add_object(staticmaps.Area([p1, p2, p3, p1], color=staticmaps.RED, fill_color=staticmaps.TRANSPARENT, width=2))
context.add_object(staticmaps.Marker(p1, color=staticmaps.BLUE))
context.add_object(staticmaps.Marker(p2, color=staticmaps.GREEN))
context.add_object(staticmaps.Marker(p3, color=staticmaps.YELLOW))

for name, provider in staticmaps.default_tile_providers.items():
    context.set_tile_provider(provider)

    # render png via pillow
    image = context.render_pillow(800, 500)
    image.save(f"provider_{name}.pillow.png")

    # render png via cairo
    if staticmaps.cairo_is_supported():
        image = context.render_cairo(800, 500)
        image.write_to_png(f"provider_{name}.cairo.png")

    # render svg
    svg_image = context.render_svg(800, 500)
    with open(f"provider_{name}.svg", "w", encoding="utf-8") as f:
        svg_image.write(f, pretty=True)
