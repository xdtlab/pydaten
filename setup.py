#!/usr/bin/env python3

from setuptools import setup

setup(name = 'pydaten',
    version = '0.1.0',
    description = 'Daten implementation in Python',
    author = 'Daten Project',
    author_email = 'daten-project@gmx.com',
    url = 'https://github.com/daten-project/pydaten',
    install_requires = ['coincurve', 'argon2_cffi', 'asyncio', 'aiohttp', 'requests'],
    packages = ['pydaten'],
    package_data = {'': ['resources/*', 'resources/static/*']},
    scripts = ['core/daten'])
