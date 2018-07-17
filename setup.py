#!/usr/bin/env python

from distutils.core import setup

setup(name='Domain Connect',
      version='0.1',
      description='Python client library for Domain Connect protocol',
      author='Pawel Kowalik',
      author_email='pawel-kow@users.noreply.github.com',
      url='https://github.com/pawel-kow/domainconnect_python',
      license='https://github.com/pawel-kow/domainconnect_python/blob/master/LICENSE',
      packages=['domainconnect',],
      install_requires=[
          'dnspython >= 1.15.0',
          'publicsuffix >= 1.1.0',
          'publicsuffixlist >= 0.6.1',
          'six >= 1.11.0'
      ],
      )
