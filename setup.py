#!/usr/bin/env python

import os
import sys

try:
  from setuptools import setup, find_packages
except ImportError:
  from distutils.core import setup, find_packages

if sys.argv[-1] == 'publish':
  os.system('python setup.py sdist upload')
  sys.exit()

readme = open('README.md').read()
doclink = """
Documentation
-------------

The full documentation is at https://github.com/huynhcongdanh/passmancli/blob/master/README.md """
history = open('CHANGELOG.rst').read().replace('.. :changelog:', '')
ver = open('VERSION.rst').read()

setup(
  name='passmancli',
  version= ver,
  description='NextCloud/OwnCloud Passman CLI. A folk of Douglas Camata original work at https://github.com/douglascamata/passmancli',
  long_description=readme + '\n\n' + doclink + '\n\n' + history,
  author='Danh Huynh',
  author_email='danhuynh.info@gmail.com',
  url='https://github.com/huynhcongdanh/passmancli',
  packages=find_packages(exclude=['docs', 'tests', 'samples']),
  entry_points={
    'console_scripts': [
      'passman = passmancli.entrypoint:main'
    ]
  },
  include_package_data=True,
  install_requires=[
    "requests",
    "pycryptodome",
    "sjcl",
    "pygments",
    "click",
    "wheel>=0.22",
    "pytest",
    "ConfigParser",
    "configparser",
    "requests",
    "sjcl"
  ],
  dependency_links=[
    "https://github.com/arnuschky/sjcl/tarball/master#egg=sjcl"
  ],
  license='MIT',
  zip_safe=False,
  keywords='passmancli, passman, security',
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Natural Language :: English',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: Implementation :: PyPy',
  ],
)
