#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2016 Óscar García Amor <ogarcia@connectical.com>
#
# Distributed under terms of the GNU GPLv3 license.

import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "fileteasend",
    version = "1.0",
    author = "Jason Brechin",
    author_email = "brechinj+github@gmail.com",
    description = ("Easy file transfer using the FileTea service"),
    license = "GPLv3",
    keywords = "file web transfer easy FileTea",
    url = "https://github.com/brechin/FileTeaSend",
    packages=['fileteasend'],
    long_description=read('README.md'),
    entry_points={
        'console_scripts': [
            'filetea = fileteasend.app:main'
        ]
    },
    install_requires = [
        "requests>=2.13.0",
        "python-magic>=0.4.0"
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: GNU General Public License (GPLv3)",
        'Programming Language :: Python :: 3',
    ],
)
