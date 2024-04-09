#!/usr/bin/env python

# py-staticmaps
# Copyright (c) 2020 Florian Pigorsch; see /LICENSE for licensing information

import staticmaps

context = staticmaps.Context()
context.set_tile_provider(staticmaps.tile_provider_ArcGISWorldImagery)

hongkong = staticmaps.create_latlng(22.308046, 113.918480)
newyork = staticmaps.create_latlng(40.641766, -73.780968)

context.add_object(staticmaps.Line([hongkong, newyork], color=staticmaps.BLUE))
context.add_object(staticmaps.Marker(hongkong, color=staticmaps.GREEN))
context.add_object(staticmaps.Marker(newyork, color=staticmaps.RED))

# render png via pillow
image = context.render_pillow(1920, 1080)
image.save("idl.pillow.png")

# render png via cairo
if staticmaps.cairo_is_supported():
    cairo_image = context.render_cairo(1920, 1080)
    cairo_image.write_to_png("idl.cairo.png")

# render svg
svg_image = context.render_svg(1920, 1080)
with open("idl.svg", "w", encoding="utf-8") as f:
    svg_image.write(f, pretty=True)
