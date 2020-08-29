import s2sphere as s2  # type: ignore
import typing


def latlng(lat: float, lng: float) -> s2.LatLng:
    return s2.LatLng.from_degrees(lat, lng)


def parse_latlng(s: str) -> s2.LatLng:
    a = s.split(",")
    if len(a) != 2:
        raise ValueError('Cannot parse coordinates string "{}" (not a comma-separated lat/lng pair)'.format(s))

    try:
        lat = float(a[0].strip())
        lng = float(a[1].strip())
    except ValueError:
        raise ValueError('Cannot parse coordinates string "{}" (non-numeric lat/lng values)'.format(s))

    if lat < -90 or lat > 90 or lng < -180 or lng > 180:
        raise ValueError('Cannot parse coordinates string "{}" (out of bounds lat/lng values)'.format(s))

    return latlng(lat, lng)


def parse_latlngs(s: str) -> typing.List[s2.LatLng]:
    res = []
    for c in s.split():
        c = c.strip()
        if len(c) > 0:
            res.append(parse_latlng(c))
    return res
