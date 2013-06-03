#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

import knickknack

with open('README.txt') as stream:
  long_desc = stream.read()

setup(
    name = knickknack.__name__,
    version = knickknack.__version__,
    author = knickknack.__author__,
    author_email = knickknack.__email__,
    packages = ['knickknack'],
    license = knickknack.__license__,
    description = knickknack.__description__,
    url='https://github.com/whardier/KnickKnack',
    long_description = long_desc,
    classifiers = [
        'Programming Language :: Python',
        'Operating System :: OS Independent',
        'Development Status :: 1 - Planning',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'License :: Other/Proprietary License',
        'Natural Language :: English',
        'Topic :: Database',
    ],
    install_requires=[
        'requests',
    ],
    entry_points={
        'console_scripts': [
            'knickknack=knickknack.__main__:main',
        ],
    },
)

