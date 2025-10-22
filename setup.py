#! /usr/bin/env python3

import os

try:
    from setuptools import find_packages, setup
except AttributeError:
    from setuptools import find_packages, setup

NAME = 'OASYS2-WOFRY'
VERSION = '1.0.9'
ISRELEASED = False

DESCRIPTION = 'WOFRY (Wave Optics FRamework in pYthon)'
README_FILE = os.path.join(os.path.dirname(__file__), 'README.md')
LONG_DESCRIPTION = open(README_FILE).read()
AUTHOR = 'Manuel Sanchez del Rio, Luca Rebuffi'
AUTHOR_EMAIL = 'lrebuffi@anl.gov'
URL = 'https://github.com/oasys-kit/OASYS2-WOFRY'
DOWNLOAD_URL = 'https://github.com/oasys-kit/OASYS2-WOFRY'
LICENSE = 'GPLv3'

KEYWORDS = [
    'simulator',
    'waveoptics',
    'oasys2',
]

CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Environment :: X11 Applications :: Qt',
    'Environment :: Console',
    'Environment :: Plugins',
    'Programming Language :: Python :: 3',
    'Intended Audience :: Science/Research',
]

SETUP_REQUIRES = (
    'setuptools',
)

INSTALL_REQUIRES = (
    'oasys2>=0.0.7',
    'syned-gui-2>=1.0.3',
    'wofryimpl>=1.0.33',
)

PACKAGES = find_packages(exclude=('*.tests', '*.tests.*', 'tests.*', 'tests'))

PACKAGE_DATA = {
    "orangecontrib.wofry.widgets.wavefront_propagation":["icons/*.png", "icons/*.jpg"],
    "orangecontrib.wofry.widgets.beamline_elements":["icons/*.png", "icons/*.jpg"],
    "orangecontrib.wofry.widgets.tools":["icons/*.png", "icons/*.jpg"],
}

ENTRY_POINTS = {
    'oasys2.addons' : ("wofry = orangecontrib.wofry", ),
    'oasys2.widgets' : (
        "Wofry Wavefront Propagation = orangecontrib.wofry.widgets.wavefront_propagation",
        "Wofry Optical Elements = orangecontrib.wofry.widgets.beamline_elements",
        "Wofry Tools = orangecontrib.wofry.widgets.tools",
    ),
}

if __name__ == '__main__':
    setup(
          name = NAME,
          version = VERSION,
          description = DESCRIPTION,
          long_description = LONG_DESCRIPTION,
          author = AUTHOR,
          author_email = AUTHOR_EMAIL,
          url = URL,
          download_url = DOWNLOAD_URL,
          license = LICENSE,
          keywords = KEYWORDS,
          classifiers = CLASSIFIERS,
          packages = PACKAGES,
          package_data = PACKAGE_DATA,
          setup_requires = SETUP_REQUIRES,
          install_requires = INSTALL_REQUIRES,
          entry_points = ENTRY_POINTS,
          include_package_data = True,
          zip_safe = False,
          )
