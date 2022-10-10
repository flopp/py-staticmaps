"""py-staticmaps - context"""
# Copyright (c) 2020 Florian Pigorsch; see /LICENSE for licensing information

import typing

import s2sphere  # type: ignore


def create_latlng(lat: float, lng: float) -> s2sphere.LatLng:
    """Create a LatLng object from float values

    Parameters:
        lat (float): latitude
        lng (float): longitude

    Returns:
        s2sphere.LatLng: LatLng object
    """
    return s2sphere.LatLng.from_degrees(lat, lng)


def parse_latlng(s: str) -> s2sphere.LatLng:
    """Parse a string with comma separated latitude,longitude values and create a LatLng object from float values

    Parameters:
        s (str): string with latitude,longitude values

    Returns:
        s2sphere.LatLng: LatLng object

    Raises:
        ValueError: raises a value error if the format is wrong
    """
    a = s.split(",")
    if len(a) != 2:
        raise ValueError(f'Cannot parse coordinates string "{s}" (not a comma-separated lat/lng pair)')

    try:
        lat = float(a[0].strip())
        lng = float(a[1].strip())
    except ValueError as e:
        raise ValueError(f'Cannot parse coordinates string "{s}" (non-numeric lat/lng values)') from e

    if lat < -90 or lat > 90 or lng < -180 or lng > 180:
        raise ValueError(f'Cannot parse coordinates string "{s}" (out of bounds lat/lng values)')

    return create_latlng(lat, lng)


def parse_latlngs(s: str) -> typing.List[s2sphere.LatLng]:
    """Parse a string with multiple comma separated latitude,longitude values and create a list of LatLng objects

    Parameters:
        s (str): string with multiple latitude,longitude values
            separated with empty space

    Returns:
        typing.List[s2sphere.LatLng]: list of LatLng objects
    """
    res = []
    for c in s.split():
        c = c.strip()
        if len(c) > 0:
            res.append(parse_latlng(c))
    return res


def parse_latlngs2rect(s: str) -> s2sphere.LatLngRect:
    """Parse a string with two comma separated latitude,longitude values and
    create a LatLngRect object

    Parameters:
        s (str): string with two latitude,longitude values separated
            with empty space

    Returns:
        s2sphere.LatLngRect: LatLngRect from LatLng pair

    Raises:
        ValueError: exactly two lat/lng pairs must be given as argument
    """
    latlngs = parse_latlngs(s)
    if len(latlngs) != 2:
        raise ValueError(f'Cannot parse coordinates string "{s}" (requires exactly two lat/lng pairs)')

    return s2sphere.LatLngRect.from_point_pair(latlngs[0], latlngs[1])
