# py-staticmaps
# Copyright (c) 2020 Florian Pigorsch; see /LICENSE for licensing information

import os
import re
import typing

import setuptools  # type: ignore


def _read_meta(rel_path: str, identifier: str) -> str:
    abs_path = os.path.join(os.path.dirname(__file__), rel_path)
    with open(abs_path) as f:
        content = f.read()
    r = r"^" + identifier + r"\s*=\s*['\"]([^'\"]*)['\"]$"
    m = re.search(r, content, re.M)
    if not m:
        raise RuntimeError(f"Unable to find {identifier} string in {rel_path}.")
    return m.group(1)


def _read_descr(rel_path: str) -> str:
    abs_path = os.path.join(os.path.dirname(__file__), rel_path)
    re_image = re.compile(r"^.*!\[.*\]\(.*\).*$")
    lines: typing.List[str] = []
    with open(abs_path) as f:
        for line in f:
            if re_image.match(line):
                continue
            lines.append(line)
    print("".join(lines))
    return "".join(lines)


def _read_reqs(rel_path: str) -> typing.List[str]:
    abs_path = os.path.join(os.path.dirname(__file__), rel_path)
    with open(abs_path) as f:
        return [s.strip() for s in f.readlines() if s.strip() and not s.strip().startswith("#")]


PACKAGE = "staticmaps"

setuptools.setup(
    name=_read_meta(f"{PACKAGE}/meta.py", "LIB_NAME"),
    version=_read_meta(f"{PACKAGE}/meta.py", "VERSION"),
    description="Create static map images (SVG, PNG) with markers, geodesic lines, ...",
    long_description=_read_descr("README.md"),
    long_description_content_type="text/markdown",
    url=_read_meta(f"{PACKAGE}/meta.py", "GITHUB_URL"),
    author="Florian Pigorsch",
    author_email="mail@florian-pigorsch.de",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: GIS",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    keywords="map staticmap osm markers",
    packages=[PACKAGE],
    install_requires=_read_reqs("requirements.txt"),
    extras_require={
        "dev": _read_reqs("requirements-dev.txt"),
        "examples": _read_reqs("requirements-examples.txt"),
    },
    entry_points={
        "console_scripts": [
            f"createstaticmap={PACKAGE}.cli:main",
        ],
    },
)
