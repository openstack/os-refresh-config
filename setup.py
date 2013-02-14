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
    'version': '0.3',
    'packages': ['os_refresh_config'],
    'scripts': [],
    'long_description': open('README.md', 'rb').read(),
    'packages': ['os_refresh_config'],
    'entry_points': {
      'console_scripts': [
          'os-refresh-config = os_refresh_config.os_refresh_config:main']
    }
}

setup(**config)
