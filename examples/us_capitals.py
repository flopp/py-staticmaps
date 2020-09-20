#!/usr/bin/env python

# py-staticmaps
# Copyright (c) 2020 Florian Pigorsch; see /LICENSE for licensing information

import json
import requests
import staticmaps

context = staticmaps.Context()
context.set_tile_provider(staticmaps.tile_provider_OSM)

URL = (
    "https://gist.githubusercontent.com/jpriebe/d62a45e29f24e843c974/"
    "raw/b1d3066d245e742018bce56e41788ac7afa60e29/us_state_capitals.json"
)
response = requests.get(URL)
for _, data in json.loads(response.text).items():
    capital = staticmaps.create_latlng(float(data["lat"]), float(data["long"]))
    context.add_object(staticmaps.Marker(capital, size=5))

# render png
image = context.render_cairo(800, 500)
image.write_to_png("us_capitals.png")

# render svg
svg_image = context.render_svg(800, 500)
with open("us_capitals.svg", "w", encoding="utf-8") as f:
    svg_image.write(f, pretty=True)
