import math
import typing

from geographiclib.geodesic import Geodesic  # type: ignore
import s2sphere  # type: ignore
import svgwrite  # type: ignore

from .color import Color, RED
from .transformer import Transformer
from .object import Object, PixelBoundsT


class Line(Object):
    def __init__(
        self,
        latlngs: typing.List[s2sphere.LatLng],
        color: Color = RED,
    ) -> None:
        Object.__init__(self)
        if latlngs is None or len(latlngs) < 2:
            raise ValueError("Trying to create line with less than 2 coordinates")
        self._latlngs = latlngs
        self.simplify()
        self._color = color
        self._interpolation_cache: typing.Optional[typing.List[s2sphere.LatLng]] = None

    def bounds(self) -> s2sphere.LatLngRect:
        b = s2sphere.LatLngRect()
        for latlng in self.interpolate():
            latlng = latlng.normalized()
            b = b.union(s2sphere.LatLngRect.from_point(latlng))
        return b

    def extra_pixel_bounds(self) -> PixelBoundsT:
        return 1, 1, 1, 1

    def simplify(self) -> None:
        last = self._latlngs[0]
        min_lat = last.lat().radians
        max_lat = min_lat
        min_lng = 0
        max_lng = 0
        for p in self._latlngs[1:]:
            min_lat = min(min_lat, p.lat().radians)
            max_lat = max(max_lat, p.lat().radians)
            d = last.lng().radians - p.lng().radians
            while d < -math.pi:
                d += 2 * math.pi
            while d > math.pi:
                d -= 2 * math.pi
            min_lng = min(min_lng, d)
            max_lng = max(max_lng, d)
        thresh_lat = 0.01 * (max_lat - min_lat)
        thresh_lng = 0.01 * (max_lng - min_lng)
        res = [last]
        for p in self._latlngs[1:-1]:
            dlat = abs(p.lat().radians - last.lat().radians)
            dlng = abs(p.lng().radians - last.lng().radians)
            if (dlat > thresh_lat) or (dlng > thresh_lng):
                last = p
                res.append(last)
        res.append(self._latlngs[-1])
        self._latlngs = res

    def interpolate(self) -> typing.List[s2sphere.LatLng]:
        if self._interpolation_cache is not None:
            return self._interpolation_cache
        self._interpolation_cache = []
        threshold = 2 * math.pi / 360
        last = self._latlngs[0]
        self._interpolation_cache.append(last)
        geod = Geodesic.WGS84
        for current in self._latlngs[1:]:
            # don't perform geodesic interpolation if the langitudinal distance is < threshold = 1°
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
            for i in range(1, n):
                a = (i * line.a13) / n
                g = line.ArcPosition(a, Geodesic.LATITUDE | Geodesic.LONGITUDE | Geodesic.LONG_UNROLL)
                self._interpolation_cache.append(s2sphere.LatLng.from_degrees(g["lat2"], g["lon2"]))
            self._interpolation_cache.append(current)
            last = current
        return self._interpolation_cache

    def render(self, transformer: Transformer, draw: svgwrite.Drawing, group: svgwrite.container.Group) -> None:
        xys = [transformer.ll2pixel(latlng) for latlng in self.interpolate()]
        x_count = math.ceil(transformer.image_width() / (2 * transformer.world_width()))
        for p in range(-x_count, x_count + 1):
            group.add(
                draw.polyline(
                    [(x + p * transformer.world_width(), y) for x, y in xys],
                    fill="none",
                    stroke=self._color.hex_string(),
                    stroke_width=2,
                )
            )
