#!/usr/bin/env python3

from setuptools import setup

setup(name = 'pydaten',
    version = '0.1.0',
    description = 'Daten implementation in Python',
    author = 'Daten Project',
    author_email = 'daten-project@protonmail.ch',
    url = 'https://github.com/xdtlab/pydaten',
    install_requires = ['coincurve', 'argon2_cffi', 'asyncio', 'aiohttp', 'requests', 'plyvel'],
    packages = ['pydaten',
                'pydaten.common',
                'pydaten.core',
                'pydaten.defaults',
                'pydaten.network',
                'pydaten.utils',
                'pydaten.crypto'],
    package_data = {'': ['resources/*', 'resources/static/*']},
    scripts = ['scripts/daten'])
