[![CI](https://github.com/flopp/py-staticmaps/workflows/CI/badge.svg)](https://github.com/flopp/py-staticmaps/actions?query=workflow%3ACI)
[![PyPI Package](https://img.shields.io/pypi/v/py-staticmaps.svg)](https://pypi.org/project/py-staticmaps/)
[![Format](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
[![License MIT](https://img.shields.io/badge/license-MIT-lightgrey.svg?style=flat)](LICENSE)

# py-staticmaps
A python module to create static map images (PNG, SVG) with markers, geodesic lines, etc.


## Features

- Map objects: pin-style markers, image (PNG) markers, polylines, polygons, (geodesic) circles
- Automatic computation of best center + zoom from the added map objects
- Several pre-configured map tile providers
- Proper tile provider attributions display
- On-disc caching of map tile images for faster drawing and reduced load on the tile servers
- Non-anti-aliased drawing via `PILLOW`
- Anti-aliased drawing via `pycairo` (optional; only if `pycairo` is installed properly)
- SVG creation via `svgwrite`


## Installation

### SVG + non-anti-aliased PNG version

```shell
pip install py-staticmaps
```

### SVG + anti-aliased PNG version (via Cairo)

```shell
pip install py-staticmaps[cairo]
```

`py-staticmaps` uses `pycairo` for creating anti-aliased raster-graphics, so make sure `libcairo2` is installed on your system (on Ubuntu just install the `libcairo2-dev` package, i.e. `sudo apt install libcairo2-dev`).


## Examples

Note: PNG support (e.g. `context.render_cairo(...)`) is only available if the `pycairo` module is installed.

### Markers and Geodesic Lines

```python
import staticmaps

context = staticmaps.Context()
context.set_tile_provider(staticmaps.tile_provider_StamenToner)

frankfurt = staticmaps.create_latlng(50.110644, 8.682092)
newyork = staticmaps.create_latlng(40.712728, -74.006015)

context.add_object(staticmaps.Line([frankfurt, newyork], color=staticmaps.BLUE, width=4))
context.add_object(staticmaps.Marker(frankfurt, color=staticmaps.GREEN, size=12))
context.add_object(staticmaps.Marker(newyork, color=staticmaps.RED, size=12))

# render non-anti-aliased png
image = context.render_pillow(800, 500)
image.save("frankfurt_newyork.pillow.png")

# render anti-aliased png (this only works if pycairo is installed)
image = context.render_cairo(800, 500)
image.write_to_png("frankfurt_newyork.cairo.png")

# render svg
svg_image = context.render_svg(800, 500)
with open("frankfurt_newyork.svg", "w", encoding="utf-8") as f:
    svg_image.write(f, pretty=True)
```

![franfurt_newyork](../assets/frankfurt_newyork.png?raw=true)


### Transparent Polygons

```python
import staticmaps

context = staticmaps.Context()
context.set_tile_provider(staticmaps.tile_provider_OSM)

freiburg_polygon = [
    (47.96881, 7.79045),
    (47.96866, 7.78610),
    (47.97134, 7.77874),
    ...
]

context.add_object(
    staticmaps.Area(
        [staticmaps.create_latlng(lat, lng) for lat, lng in freiburg_polygon],
        fill_color=staticmaps.parse_color("#00FF003F"),
        width=2,
        color=staticmaps.BLUE,
    )
)

# render non-anti-aliased png
image = context.render_pillow(800, 500)
image.save("freiburg_area.pillow.png")

# render anti-aliased png (this only works if pycairo is installed)
image = context.render_cairo(800, 500)
image.write_to_png("freiburg_area.cairo.png")

# render svg
svg_image = context.render_svg(800, 500)
with open("freiburg_area.svg", "w", encoding="utf-8") as f:
    svg_image.write(f, pretty=True)
```

![freiburg_area](../assets/freiburg_area.png?raw=true)


### Drawing a GPX Track + Image Marker (PNG)

```python
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

for p in gpx.walk(only_points=True):
    pos = staticmaps.create_latlng(p.latitude, p.longitude)
    marker = staticmaps.ImageMarker(pos, "start.png", origin_x=27, origin_y=35)
    context.add_object(marker)
    break

# render non-anti-aliased png
image = context.render_pillow(800, 500)
image.save("draw_gpx.pillow.png")

# render anti-aliased png (this only works if pycairo is installed)
image = context.render_cairo(800, 500)
image.write_to_png("draw_gpx.cairo.png")
```

![draw_gpx](../assets/draw_gpx.png?raw=true)


### US State Capitals

```python
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

# render non-anti-aliased png
image = context.render_pillow(800, 500)
image.save("us_capitals.pillow.png")

# render anti-aliased png (this only works if pycairo is installed)
image = context.render_cairo(800, 500)
image.write_to_png("us_capitals.cairo.png")
```

![us_capitals](../assets/us_capitals.png?raw=true)


### Geodesic Circles

```python
import staticmaps

context = staticmaps.Context()
context.set_tile_provider(staticmaps.tile_provider_StamenToner)

center1 = staticmaps.create_latlng(66, 0)
center2 = staticmaps.create_latlng(0, 0)

context.add_object(staticmaps.Circle(center1, 2000, fill_color=staticmaps.TRANSPARENT, color=staticmaps.RED, width=2))
context.add_object(staticmaps.Circle(center2, 2000, fill_color=staticmaps.TRANSPARENT, color=staticmaps.GREEN, width=2))
context.add_object(staticmaps.Marker(center1, color=staticmaps.RED))
context.add_object(staticmaps.Marker(center2, color=staticmaps.GREEN))

# render non-anti-aliased png
image = context.render_pillow(800, 500)
image.save("geodesic_circles.pillow.png")

# render anti-aliased png (this only works if pycairo is installed)
image = context.render_cairo(800, 600)
image.write_to_png("geodesic_circles.cairo.png")
```

![geodesic_circles](../assets/geodesic_circles.png?raw=true)


### Other Examples

Please take a look at the command line program which uses the `staticmaps` package: `staticmaps/cli.py`


### Dependencies

`py-staticmaps` uses

- `PILLOW` for rendering raster-graphics
- `pycairo` for rendering antialiased raster-graphics (optional!)
- `svgwrite` for writing SVG files
- `s2sphere` for geo coordinates handling
- `geographiclib` for geodesic computations
- `appdirs` for finding the user's default cache directory
- `requests` for downloading tile files


## License

[MIT](LICENSE) &copy; 2020-2021 Florian Pigorsch
