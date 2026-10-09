# py-staticmaps
# Copyright (c) 2020 Florian Pigorsch; see /LICENSE for licensing information

import xml.etree.ElementTree as ET

import staticmaps


def test_dash_array_is_serialized_on_area_outline() -> None:
    points = [
        staticmaps.create_latlng(0, 0),
        staticmaps.create_latlng(0, 0.5),
        staticmaps.create_latlng(0.5, 0.5),
    ]
    renderer = staticmaps.SvgRenderer(staticmaps.Transformer(200, 100, 8, points[0], 256))
    renderer.render_objects([staticmaps.Area(points, color=staticmaps.BLUE, width=2, dash_array=[10, 5])])

    root = ET.fromstring(renderer.drawing().tostring())
    outline = root.find(".//{http://www.w3.org/2000/svg}polygon[@stroke-dasharray]")

    assert outline is not None
    assert outline.get("fill") == "none"
    assert outline.get("stroke-dasharray") == "10,5"


def test_tiny_closed_dashed_outline_remains_visible_in_pillow() -> None:
    transformer = staticmaps.Transformer(40, 40, 12, staticmaps.create_latlng(0, 0), 256)
    points = [
        transformer.pixel2ll(10, 10),
        transformer.pixel2ll(10.1, 10),
        transformer.pixel2ll(10.1, 10.1),
        transformer.pixel2ll(10, 10.1),
    ]
    renderer = staticmaps.PillowRenderer(transformer)
    renderer.render_objects(
        [
            staticmaps.Area(
                points,
                fill_color=staticmaps.TRANSPARENT,
                color=staticmaps.BLUE,
                width=4,
                dash_array=[10, 5],
            )
        ]
    )

    bounds = renderer.image().getbbox()
    assert bounds is not None
    assert bounds[2] - bounds[0] >= 4
    assert bounds[3] - bounds[1] >= 4
