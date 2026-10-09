# py-staticmaps
# Copyright (c) 2020 Florian Pigorsch; see /LICENSE for licensing information

import math
import typing

from geographiclib.geodesic import Geodesic  # type: ignore
import s2sphere  # type: ignore

from .color import Color, RED
from .coordinates import create_latlng
from .object import Object, PixelBoundsT
from .cairo_renderer import CairoRenderer
from .pillow_renderer import PillowRenderer
from .svg_renderer import SvgRenderer


class Line(Object):
    def __init__(
        self,
        latlngs: typing.List[s2sphere.LatLng],
        color: Color = RED,
        width: int = 2,
        dash_array: typing.Optional[typing.Sequence[float]] = None,
    ) -> None:
        Object.__init__(self)
        if latlngs is None or len(latlngs) < 2:
            raise ValueError("Trying to create line with less than 2 coordinates")
        if width < 0:
            raise ValueError(f"'width' must be >= 0: {width}")
        if dash_array is not None and any(not math.isfinite(length) or length <= 0 for length in dash_array):
            raise ValueError("'dash_array' values must be finite and > 0")

        self._latlngs = latlngs
        self._color = color
        self._width = width
        self._dash_array = list(dash_array) if dash_array else None
        self._interpolation_cache: typing.Optional[typing.List[s2sphere.LatLng]] = None

    def color(self) -> Color:
        """Return color of the line

        :return: color object
        :rtype: Color
        """
        return self._color

    def width(self) -> int:
        """Return width of line

        :return: width
        :rtype: int
        """
        return self._width

    def dash_array(self) -> typing.Optional[typing.List[float]]:
        """Return the dash and gap lengths for the line stroke, in pixels."""
        return self._dash_array

    def bounds(self) -> s2sphere.LatLngRect:
        """Return bounds of line

        :return: bounds of line
        :rtype: s2sphere.LatLngRect
        """
        b = s2sphere.LatLngRect()
        for latlng in self.interpolate():
            b = b.union(s2sphere.LatLngRect.from_point(latlng.normalized()))
        return b

    def extra_pixel_bounds(self) -> PixelBoundsT:
        """Return extra pixel bounds from line

        :return: extra pixel bounds
        :rtype: PixelBoundsT
        """
        return self._width, self._width, self._width, self._width

    def interpolate(self) -> typing.List[s2sphere.LatLng]:
        """Interpolate bounds

        :return: list of LatLng
        :rtype: typing.List[s2sphere.LatLng]
        """
        if self._interpolation_cache is not None:
            return self._interpolation_cache
        assert len(self._latlngs) >= 2
        self._interpolation_cache = []
        threshold = 2 * math.pi / 360
        last = self._latlngs[0]
        self._interpolation_cache.append(last)
        geod = Geodesic.WGS84
        for current in self._latlngs[1:]:
            # don't perform geodesic interpolation if the longitudinal distance is < threshold = 1°
            dlng = current.lng().radians - last.lng().radians
            while dlng < 0:
                dlng += 2 * math.pi
            while dlng >= math.pi:
                dlng -= 2 * math.pi
            if abs(dlng) < threshold:
                self._interpolation_cache.append(current)
                last = current
                continue
            # geodesic interpolation
            line = geod.InverseLine(
                last.lat().degrees,
                last.lng().degrees,
                current.lat().degrees,
                current.lng().degrees,
            )
            n = 2 + math.ceil(line.a13)
            for i in range(1, n + 1):
                a = (i * line.a13) / n
                g = line.ArcPosition(a, Geodesic.LATITUDE | Geodesic.LONGITUDE | Geodesic.LONG_UNROLL)
                self._interpolation_cache.append(create_latlng(g["lat2"], g["lon2"]))
            last = current
        return self._interpolation_cache

    def render_pillow(self, renderer: PillowRenderer) -> None:
        """Render line using PILLOW

        :param renderer: pillow renderer
        :type renderer: PillowRenderer
        """
        if self.width() == 0:
            return
        xys = [
            (x + renderer.offset_x(), y)
            for (x, y) in [renderer.transformer().ll2pixel(latlng) for latlng in self.interpolate()]
        ]
        if self.dash_array() is None:
            renderer.draw().line(xys, self.color().int_rgba(), self.width())
            return
        bounds = (
            -self.width(),
            -self.width(),
            renderer.image().width + self.width(),
            renderer.image().height + self.width(),
        )
        _draw_pillow_dashes(
            renderer.draw(),
            xys,
            self.dash_array(),
            bounds=bounds,
            fill=self.color().int_rgba(),
            width=self.width(),
        )

    def render_svg(self, renderer: SvgRenderer) -> None:
        """Render line using svgwrite

        :param renderer: svg renderer
        :type renderer: SvgRenderer
        """
        if self.width() == 0:
            return
        xys = [renderer.transformer().ll2pixel(latlng) for latlng in self.interpolate()]
        dash_array = self.dash_array()
        polyline = renderer.drawing().polyline(
            xys,
            fill="none",
            stroke=self.color().hex_rgb(),
            stroke_width=self.width(),
            opacity=self.color().float_a(),
            **({"stroke_dasharray": ",".join(str(length) for length in dash_array)} if dash_array is not None else {}),
        )
        renderer.group().add(polyline)

    def render_cairo(self, renderer: CairoRenderer) -> None:
        """Render line using cairo

        :param renderer: cairo renderer
        :type renderer: CairoRenderer
        """
        if self.width() == 0:
            return
        xys = [renderer.transformer().ll2pixel(latlng) for latlng in self.interpolate()]
        renderer.context().set_source_rgba(*self.color().float_rgba())
        renderer.context().set_line_width(self.width())
        renderer.context().set_dash(self.dash_array() or [])
        renderer.context().new_path()
        renderer.context().move_to(*xys[0])
        for x, y in xys[1:]:
            renderer.context().line_to(x, y)
        renderer.context().stroke()


# pylint: disable=too-many-branches,too-many-locals,too-many-statements
def _dash_segments(
    points: typing.Sequence[typing.Tuple[float, float]],
    dash_array: typing.Optional[typing.Sequence[float]],
    bounds: typing.Tuple[float, float, float, float],
    close: bool = False,
) -> typing.Iterator[
    typing.Tuple[
        typing.Sequence[typing.Tuple[float, float]],
        typing.Tuple[float, float],
    ]
]:
    """Yield visible dash segments without processing portions outside the image."""
    if dash_array is None or len(points) < 2:
        return

    pattern = list(dash_array)
    if len(pattern) % 2:
        pattern *= 2
    edges = list(zip(points, points[1:]))
    if close and len(points) > 1:
        edges.append((points[-1], points[0]))

    position_in_pattern = 0.0
    pattern_index = 0
    active_points: typing.List[typing.Tuple[float, float]] = []
    active_tangent = (0.0, 0.0)
    for index, (start, end) in enumerate(edges):
        edge_length = math.hypot(end[0] - start[0], end[1] - start[1])
        if edge_length == 0:
            continue
        vector = end[0] - start[0], end[1] - start[1]
        clipped_edge = _clip_line_segment(start, end, bounds)
        if clipped_edge is None:
            if active_points:
                yield _finish_dash_run(active_points, active_tangent, trim_end=False)
                active_points = []
            pattern_index, position_in_pattern = _advance_dash_pattern(
                pattern_index, position_in_pattern, edge_length, pattern
            )
            continue

        visible_start_position = edge_length * clipped_edge[0]
        visible_end_position = edge_length * clipped_edge[1]
        clipped_start = _segment_point(start, vector, clipped_edge[0])
        clipped_end = _segment_point(start, vector, clipped_edge[1])
        visible_vector = clipped_end[0] - clipped_start[0], clipped_end[1] - clipped_start[1]
        visible_length = visible_end_position - visible_start_position
        edge_position = visible_start_position
        if edge_position > 0:
            if active_points:
                yield _finish_dash_run(active_points, active_tangent, trim_end=False)
                active_points = []
            pattern_index, position_in_pattern = _advance_dash_pattern(
                pattern_index, position_in_pattern, edge_position, pattern
            )
        while edge_position < visible_end_position:
            pattern_remaining = pattern[pattern_index] - position_in_pattern
            length = min(pattern_remaining, visible_end_position - edge_position)
            piece_start = _segment_point(
                clipped_start, visible_vector, (edge_position - visible_start_position) / visible_length
            )
            piece_end = _segment_point(
                clipped_start,
                visible_vector,
                (edge_position + length - visible_start_position) / visible_length,
            )

            if pattern_index % 2 == 0:
                if (
                    active_points
                    and math.hypot(active_points[-1][0] - piece_start[0], active_points[-1][1] - piece_start[1]) > 1e-7
                ):
                    yield _finish_dash_run(active_points, active_tangent, trim_end=False)
                    active_points = []
                if not active_points:
                    active_points.append(piece_start)
                if piece_start != piece_end:
                    active_points.append(piece_end)
                active_tangent = vector
            elif active_points:
                yield _finish_dash_run(active_points, active_tangent, trim_end=False)
                active_points = []

            edge_position += length
            position_in_pattern += length
            pattern_ends = position_in_pattern >= pattern[pattern_index] - 1e-9
            path_ends = not close and index == len(edges) - 1 and edge_position >= edge_length - 1e-9
            if pattern_ends or path_ends:
                trim_end = pattern_index % 2 == 0 and (pattern_ends or path_ends)
                if pattern_index % 2 == 0 and active_points:
                    yield _finish_dash_run(active_points, active_tangent, trim_end=trim_end)
                    active_points = []
            if pattern_ends:
                pattern_index = (pattern_index + 1) % len(pattern)
                position_in_pattern = 0.0
        if clipped_edge[1] < 1.0:
            if active_points:
                yield _finish_dash_run(active_points, active_tangent, trim_end=False)
                active_points = []
            pattern_index, position_in_pattern = _advance_dash_pattern(
                pattern_index, position_in_pattern, edge_length * (1.0 - clipped_edge[1]), pattern
            )

    if active_points:
        yield _finish_dash_run(active_points, active_tangent, trim_end=False)


def _advance_dash_pattern(
    pattern_index: int,
    position_in_pattern: float,
    distance: float,
    pattern: typing.Sequence[float],
) -> typing.Tuple[int, float]:
    cycle_length = sum(pattern)
    position = (sum(pattern[:pattern_index]) + position_in_pattern + distance) % cycle_length
    pattern_index = 0
    while position >= pattern[pattern_index]:
        position -= pattern[pattern_index]
        pattern_index += 1
    return pattern_index, position


def _clip_line_segment(
    start: typing.Tuple[float, float],
    end: typing.Tuple[float, float],
    bounds: typing.Tuple[float, float, float, float],
) -> typing.Optional[typing.Tuple[float, float]]:
    """Return the visible portion of a line as start/end ratios, if it crosses the bounds."""
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    left, top, right, bottom = bounds
    t_start = 0.0
    t_end = 1.0
    for p_value, q_value in (
        (-dx, start[0] - left),
        (dx, right - start[0]),
        (-dy, start[1] - top),
        (dy, bottom - start[1]),
    ):
        if p_value == 0:
            if q_value < 0:
                return None
            continue
        ratio = q_value / p_value
        if p_value < 0:
            t_start = max(t_start, ratio)
        else:
            t_end = min(t_end, ratio)
        if t_start > t_end:
            return None
    return t_start, t_end


def _finish_dash_run(
    points: typing.List[typing.Tuple[float, float]],
    tangent: typing.Tuple[float, float],
    *,
    trim_end: bool,
) -> typing.Tuple[typing.Sequence[typing.Tuple[float, float]], typing.Tuple[float, float]]:
    if trim_end and _dash_path_length(points) <= 1 and _has_direction_change(points):
        return points, (points[-1][0] - points[-2][0], points[-1][1] - points[-2][1])
    if trim_end:
        remaining = 1.0
        while len(points) > 1 and remaining > 0:
            previous = points[-2]
            end = points[-1]
            length = math.hypot(end[0] - previous[0], end[1] - previous[1])
            if length <= remaining:
                points.pop()
                remaining -= length
            else:
                ratio = (length - remaining) / length
                points[-1] = _segment_point(previous, (end[0] - previous[0], end[1] - previous[1]), ratio)
                remaining = 0
    if len(points) > 1:
        tangent = points[-1][0] - points[-2][0], points[-1][1] - points[-2][1]
    return points, tangent


def _dash_path_length(points: typing.Sequence[typing.Tuple[float, float]]) -> float:
    return sum(math.hypot(end[0] - start[0], end[1] - start[1]) for start, end in zip(points, points[1:]))


def _has_direction_change(points: typing.Sequence[typing.Tuple[float, float]]) -> bool:
    threshold = math.sin(math.pi / 36)
    reference_vector: typing.Optional[typing.Tuple[float, float]] = None
    for start, end in zip(points, points[1:]):
        vector = end[0] - start[0], end[1] - start[1]
        length = math.hypot(*vector)
        if length == 0:
            continue
        if reference_vector is not None:
            reference_length = math.hypot(*reference_vector)
            cross = reference_vector[0] * vector[1] - reference_vector[1] * vector[0]
            dot = reference_vector[0] * vector[0] + reference_vector[1] * vector[1]
            if dot < 0 or abs(cross) > threshold * reference_length * length:
                return True
        else:
            reference_vector = vector
    return False


def _segment_point(
    start: typing.Tuple[float, float],
    vector: typing.Tuple[float, float],
    ratio: float,
) -> typing.Tuple[float, float]:
    return start[0] + vector[0] * ratio, start[1] + vector[1] * ratio


def _draw_pillow_dashes(
    draw: typing.Any,
    points: typing.Sequence[typing.Tuple[float, float]],
    pattern: typing.Optional[typing.Sequence[float]],
    *,
    bounds: typing.Tuple[float, float, float, float],
    fill: typing.Tuple[int, int, int, int],
    width: int,
    close: bool = False,
) -> None:
    """Draw Pillow dashes without collapsing short runs to one-pixel dots."""
    for dash_points, (dx, dy) in _dash_segments(points, pattern, bounds, close):
        path_length = _dash_path_length(dash_points)
        endpoints_differ = (int(dash_points[0][0]), int(dash_points[0][1])) != (
            int(dash_points[-1][0]),
            int(dash_points[-1][1]),
        )
        if path_length > 1 or (len(dash_points) > 1 and endpoints_differ):
            draw.line(dash_points, fill=fill, width=width)
            continue
        if len(dash_points) > 1 and _has_direction_change(dash_points):
            for start, end in zip(dash_points, dash_points[1:]):
                dx = end[0] - start[0]
                dy = end[1] - start[1]
                length = math.hypot(dx, dy)
                if length:
                    normal = (-dy / length, dx / length)
                    half_width = max(0.0, (width - 1) / 2)
                    draw.line(
                        [
                            (start[0] - normal[0] * half_width, start[1] - normal[1] * half_width),
                            (start[0] + normal[0] * half_width, start[1] + normal[1] * half_width),
                        ],
                        fill=fill,
                        width=1,
                    )
            continue
        length = math.hypot(dx, dy)
        if length:
            start = dash_points[0]
            half_width = max(0.0, (width - 1) / 2)
            normal = (-dy / length, dx / length)
            draw.line(
                [
                    (
                        start[0] - normal[0] * half_width,
                        start[1] - normal[1] * half_width,
                    ),
                    (
                        start[0] + normal[0] * half_width,
                        start[1] + normal[1] * half_width,
                    ),
                ],
                fill=fill,
                width=1,
            )
