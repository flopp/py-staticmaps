import typing

import s2sphere  # type: ignore


def latlng(lat: float, lng: float) -> s2sphere.LatLng:
    return s2sphere.LatLng.from_degrees(lat, lng)


def parse_latlng(s: str) -> s2sphere.LatLng:
    a = s.split(",")
    if len(a) != 2:
        raise ValueError('Cannot parse coordinates string "{}" (not a comma-separated lat/lng pair)'.format(s))

    try:
        lat = float(a[0].strip())
        lng = float(a[1].strip())
    except ValueError as e:
        raise ValueError('Cannot parse coordinates string "{}" (non-numeric lat/lng values)'.format(s)) from e

    if lat < -90 or lat > 90 or lng < -180 or lng > 180:
        raise ValueError('Cannot parse coordinates string "{}" (out of bounds lat/lng values)'.format(s))

    return latlng(lat, lng)


def parse_latlngs(s: str) -> typing.List[s2sphere.LatLng]:
    res = []
    for c in s.split():
        c = c.strip()
        if len(c) > 0:
            res.append(parse_latlng(c))
    return res
