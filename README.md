[![CI](https://github.com/flopp/py-staticmaps/workflows/CI/badge.svg)](https://github.com/flopp/py-staticmaps/actions?query=workflow%3ACI)
[![Format](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
[![License MIT](https://img.shields.io/badge/license-MIT-lightgrey.svg?style=flat)]((https://github.com/flopp/py-staticmaps/blob/master/LICENSE))

# py-staticmaps
A python module to create static map images (PNG, SVG) with markers, geodesic lines, etc.


## Installation

```
pip install py-staticmaps
```


## Examples


### Markers and Geodesic Lines

```
import staticmaps

context = staticmaps.Context()
context.set_tile_provider(staticmaps.tile_provider_StamenToner)

frankfurt = staticmaps.create_latlng(50.110644, 8.682092)
newyork = staticmaps.create_latlng(40.712728, -74.006015)

context.add_object(staticmaps.Line([frankfurt, newyork], color=staticmaps.BLUE, width=4))
context.add_object(staticmaps.Marker(frankfurt, color=staticmaps.GREEN, size=12))
context.add_object(staticmaps.Marker(newyork, color=staticmaps.RED, size=12))

image = context.render_cairo(800, 500)
image.write_to_png("frankfurt_newyork.png")
```

![franfurt_newyork](../assets/franfurt_newyork.png?raw=true)


### Drawing a GPX Track

```
import sys

import gpxpy
import staticmaps

context = staticmaps.Context()
context.set_tile_provider(staticmaps.tile_provider_ArcGISWorldImagery)

with open(sys.argv[1], "r") as file:
    gpx = gpxpy.parse(file)

for track in gpx.tracks:
    for segment in track.segments:
        line = [staticmaps.create_latlng(p.latitude, p.longitude) for p in segment.points]
        context.add_object(staticmaps.Line(line))

image = context.render_cairo(800, 500)
image.write_to_png("draw_gpx.png")
```

![draw_gpx](../assets/draw_gpx.png?raw=true)


### US State Capitals

```
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

image = context.render_cairo(800, 500)
image.write_to_png("us_capitals.png")
```

![us_capitals](../assets/us_capitals.png?raw=true)


## License

[MIT](https://github.com/flopp/py-staticmaps/blob/master/LICENSE) &copy; 2016-2020 Florian Pigorsch
