# py-staticmaps
# Copyright (c) 2020 Florian Pigorsch; see /LICENSE for licensing information

import typing

from geographiclib.geodesic import Geodesic  # type: ignore
import s2sphere  # type: ignore

from .area import Area
from .color import Color, RED, TRANSPARENT
from .coordinates import create_latlng


class Circle(Area):
    """Render a circle using different renderers

    :param master: an area object
    """

    def __init__(
        self,
        center: s2sphere.LatLng,
        radius_km: float,
        fill_color: Color = RED,
        color: Color = TRANSPARENT,
        width: int = 0,
    ) -> None:
        Area.__init__(self, list(Circle.compute_circle(center, radius_km)), fill_color, color, width)

    @staticmethod
    def compute_circle(center: s2sphere.LatLng, radius_km: float) -> typing.Iterator[s2sphere.LatLng]:
        """Compute a circle with given center and radius

        :param center: Center of the circle
        :param radius_km: Radius of the circle
        :type center: s2sphere.LatLng
        :type radius_km: float

        :return: circle
        :rtype: typing.Iterator[s2sphere.LatLng]
        """
        first = None
        delta_angle = 0.1
        angle = 0.0
        geod = Geodesic.WGS84
        while angle < 360.0:
            d = geod.Direct(
                center.lat().degrees,
                center.lng().degrees,
                angle,
                radius_km * 1000.0,
                Geodesic.LONGITUDE | Geodesic.LATITUDE | Geodesic.LONG_UNROLL,
            )
            latlng = create_latlng(d["lat2"], d["lon2"])
            if first is None:
                first = latlng
            yield latlng
            angle = angle + delta_angle
        if first:
            yield first
