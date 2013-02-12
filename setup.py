#!/usr/bin/python
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'name': 'os-refresh-config',
    'description': 'refreshes system configuration',
    'author': 'SpamapS',
    'author_email': 'clint@fewbar.com',
    'url': 'http://github.com/tripleo/os-refresh-config',
    'version': '0.1',
    'packages': [],
    'scripts': ['os-refresh-config'],
    'long_description': open('README.md', 'rb').read(),
}

setup(**config)
