# py-staticmaps
# Copyright (c) 2020 Florian Pigorsch; see /LICENSE for licensing information

import typing

import pytest
from PIL import Image, ImageDraw

import staticmaps
from staticmaps.line import _draw_pillow_dashes
from staticmaps.pillow_renderer import PillowRenderer
from staticmaps.transformer import Transformer


def test_bad_creation() -> None:
    with pytest.raises(ValueError):
        staticmaps.Line([])

    with pytest.raises(ValueError):
        staticmaps.Line([staticmaps.create_latlng(48, 8)])

    with pytest.raises(ValueError):
        staticmaps.Line(
            [staticmaps.create_latlng(48, 8), staticmaps.create_latlng(49, 9)],
            width=-123,
        )


def test_creation() -> None:
    staticmaps.Line(
        [
            staticmaps.create_latlng(48, 8),
            staticmaps.create_latlng(49, 9),
            staticmaps.create_latlng(50, 8),
        ],
        color=staticmaps.YELLOW,
    )


def test_bounds() -> None:
    line = staticmaps.Line(
        [
            staticmaps.create_latlng(48, 8),
            staticmaps.create_latlng(49, 9),
            staticmaps.create_latlng(50, 8),
        ],
        color=staticmaps.YELLOW,
    )
    assert not line.bounds().is_point()


def test_dash_array_preserves_one_pixel_gaps_in_pillow() -> None:
    start = staticmaps.create_latlng(0, 0)
    end = staticmaps.create_latlng(0, 0.5)
    transformer = Transformer(200, 100, 8, start, 256)
    renderer = PillowRenderer(transformer)
    renderer.render_objects([staticmaps.Line([start, end], width=1, dash_array=[1, 1])])

    row = [
        typing.cast(typing.Tuple[int, int, int, int], renderer.image().getpixel((x, 50)))[3] > 0
        for x in range(100, 110)
    ]
    assert row == [True, False] * 5


def test_dense_fractional_vertices_preserve_pillow_dash_gaps() -> None:
    bounds = (0, 0, 60, 30)
    color = (0, 0, 0, 255)
    simple = Image.new("RGBA", (60, 30))
    dense = Image.new("RGBA", (60, 30))
    _draw_pillow_dashes(
        ImageDraw.Draw(simple),
        [(10.25, 15), (50.25, 15)],
        [1, 1],
        bounds=bounds,
        fill=color,
        width=1,
    )
    _draw_pillow_dashes(
        ImageDraw.Draw(dense),
        [(10.25 + index * 0.1, 15) for index in range(401)],
        [1, 1],
        bounds=bounds,
        fill=color,
        width=1,
    )

    simple_row = [typing.cast(typing.Tuple[int, int, int, int], simple.getpixel((x, 15)))[3] > 0 for x in range(10, 50)]
    dense_row = [typing.cast(typing.Tuple[int, int, int, int], dense.getpixel((x, 15)))[3] > 0 for x in range(10, 50)]
    assert dense_row == simple_row


def test_clipped_pillow_dashes_keep_the_original_phase() -> None:
    image = Image.new("RGBA", (60, 30))
    _draw_pillow_dashes(
        ImageDraw.Draw(image),
        [(-1_000_000, 15), (60, 15)],
        [1, 1],
        bounds=(-1, -1, 61, 31),
        fill=(0, 0, 0, 255),
        width=1,
    )

    row = [typing.cast(typing.Tuple[int, int, int, int], image.getpixel((x, 15)))[3] > 0 for x in range(10)]
    assert row == [True, False] * 5


def test_dash_array_is_serialized_in_svg() -> None:
    start = staticmaps.create_latlng(0, 0)
    end = staticmaps.create_latlng(0, 0.5)
    renderer = staticmaps.SvgRenderer(Transformer(200, 100, 8, start, 256))
    renderer.render_objects([staticmaps.Line([start, end], width=1, dash_array=[10, 5])])

    svg = renderer.drawing().tostring()
    assert 'stroke-dasharray="10,5"' in svg


def test_short_dashes_preserve_pillow_stroke_width() -> None:
    image = Image.new("RGBA", (40, 20))
    _draw_pillow_dashes(
        ImageDraw.Draw(image),
        [(10, 10), (30, 10)],
        [1.5, 1.5],
        bounds=(0, 0, 40, 20),
        fill=(0, 0, 0, 255),
        width=4,
    )

    assert sum(typing.cast(typing.Tuple[int, int, int, int], image.getpixel((10, y)))[3] > 0 for y in range(20)) == 4


def test_short_dashes_keep_both_directions_at_a_bend() -> None:
    image = Image.new("RGBA", (40, 50))
    _draw_pillow_dashes(
        ImageDraw.Draw(image),
        [(10, 20), (10.5, 20), (10.5, 40)],
        [1, 1],
        bounds=(0, 0, 40, 50),
        fill=(0, 0, 0, 255),
        width=8,
    )

    assert typing.cast(typing.Tuple[int, int, int, int], image.getpixel((10, 17)))[3] > 0
    assert typing.cast(typing.Tuple[int, int, int, int], image.getpixel((7, 20)))[3] > 0


def test_collinear_vertices_do_not_collapse_pillow_dashes() -> None:
    bounds = (0, 0, 120, 20)
    color = (0, 0, 0, 255)
    simple = Image.new("RGBA", (120, 20))
    dense = Image.new("RGBA", (120, 20))
    _draw_pillow_dashes(
        ImageDraw.Draw(simple),
        [(10, 10), (110, 10)],
        [1000, 10],
        bounds=bounds,
        fill=color,
        width=4,
    )
    _draw_pillow_dashes(
        ImageDraw.Draw(dense),
        [(10 + index, 10 + (index % 2) * 0.02) for index in range(101)],
        [1000, 10],
        bounds=bounds,
        fill=color,
        width=4,
    )

    painted_rows = [
        y for y in range(20) if typing.cast(typing.Tuple[int, int, int, int], dense.getpixel((50, y)))[3] > 0
    ]
    assert painted_rows == [9, 10, 11, 12]


def test_dash_phase_follows_nonuniform_source_path() -> None:
    points = [(10 + index, 30 + (index % 2) * 0.2) for index in range(501)]
    points.extend((10 + index, 30) for index in range(501, 1001))
    image = Image.new("RGBA", (1030, 80))

    _draw_pillow_dashes(
        ImageDraw.Draw(image),
        points,
        [10, 5],
        bounds=(0, 0, 1030, 80),
        fill=(0, 0, 0, 255),
        width=4,
    )

    assert typing.cast(typing.Tuple[int, int, int, int], image.getpixel((512, 30)))[3] > 0


def test_closed_area_dashes_use_closing_edge_direction() -> None:
    class RecordingDraw:
        def __init__(self) -> None:
            self.calls: typing.List[
                typing.Tuple[
                    typing.Sequence[typing.Tuple[float, float]],
                    typing.Dict[str, typing.Any],
                ]
            ] = []

        def line(self, points: typing.Sequence[typing.Tuple[float, float]], **kwargs: typing.Any) -> None:
            self.calls.append((points, kwargs))

    draw = RecordingDraw()
    _draw_pillow_dashes(
        draw,
        [(10, 10), (50, 10), (50, 50)],
        [1, 1],
        bounds=(0, 0, 70, 70),
        fill=(0, 0, 0, 255),
        width=4,
        close=True,
    )

    diagonal_short_strokes = []
    for points, kwargs in draw.calls:
        if kwargs["width"] != 1:
            continue
        start, end = points
        center = ((start[0] + end[0]) / 2, (start[1] + end[1]) / 2)
        if 15 < center[0] < 45 and abs(center[0] - center[1]) < 0.1:
            diagonal_short_strokes.append((end[0] - start[0], end[1] - start[1]))

    assert diagonal_short_strokes
    assert all(abs(dx) > 0 and abs(dy) > 0 for dx, dy in diagonal_short_strokes)


def test_crossing_dashes_use_the_current_edge_direction() -> None:
    class RecordingDraw:
        def __init__(self) -> None:
            self.calls: typing.List[
                typing.Tuple[
                    typing.Sequence[typing.Tuple[float, float]],
                    typing.Dict[str, typing.Any],
                ]
            ] = []

        def line(self, points: typing.Sequence[typing.Tuple[float, float]], **kwargs: typing.Any) -> None:
            self.calls.append((points, kwargs))

    draw = RecordingDraw()
    _draw_pillow_dashes(
        draw,
        [(7, 30), (50, 30), (20, 70), (20, 10)],
        [1, 6],
        bounds=(0, 0, 80, 80),
        fill=(0, 0, 0, 255),
        width=4,
    )

    crossing_strokes = []
    for points, kwargs in draw.calls:
        if kwargs["width"] != 1:
            continue
        start, end = points
        center = ((start[0] + end[0]) / 2, (start[1] + end[1]) / 2)
        if abs(center[0] - 20) < 0.1 and abs(center[1] - 30) < 0.1:
            crossing_strokes.append((end[0] - start[0], end[1] - start[1]))

    assert crossing_strokes
    assert all(abs(dx) > 0 and dy == 0 for dx, dy in crossing_strokes)
