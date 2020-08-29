import os
import re
from setuptools import setup, find_packages


def _read_version(rel_path):
    abs_path = os.path.join(os.path.dirname(__file__), rel_path)
    with open(abs_path) as f:
        content = f.read()
    r = r"^__version__ = ['\"]([^'\"]*)['\"]$"
    m = re.search(r, content, re.M)
    if not m:
        raise RuntimeError(f"Unable to find version string in {rel_path}.")
    return m.group(1)

def _read_descr(rel_path):
    abs_path = os.path.join(os.path.dirname(__file__), rel_path)
    with open(abs_path) as f:
        return f.read()

def _read_reqs(rel_path):
    abs_path = os.path.join(os.path.dirname(__file__), rel_path)
    with open(abs_path) as f:
        return [
            s.strip()
            for s in f.readlines()
            if s.strip() and not s.strip().startswith("#")
        ]

setup(
    name='py-staticmaps',
    version=_read_version("staticmaps/version.py"),
    description='Create static map images with markers, geodesic lines, ...',
    long_description=_read_descr("README.md"),
    url='https://github.com/flopp/py-staticmaps',
    author='Florian Pigorsch',
    author_email='mail@florian-pigorsch.de',

    classifiers=[
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Scientific/Engineering :: GIS',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],

    keywords='map staticmap osm markers',

    packages=['staticmaps'],

    install_requires=_read_reqs("requirements.txt"),
    extras_require={
        'dev': _read_reqs("requirements-dev.txt"),
    },
    entry_points={
        'console_scripts': [
            'staticmaps=staticmaps.cli:main',
        ],
    },
)
