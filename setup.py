#!/usr/bin/env python

from setuptools import setup

setup(name='domain_connect',
      version='0.0.1',
      description='Python client library for Domain Connect protocol. See: https://domainconnect.org',
      author='Pawel Kowalik',
      author_email='pawel-kow@users.noreply.github.com',
      url='https://github.com/pawel-kow/domainconnect_python',
      license='https://github.com/pawel-kow/domainconnect_python/blob/master/LICENSE',
      packages=['domainconnect', ],
      install_requires=[
          'dnspython >= 1.15.0',
          'publicsuffix >= 1.1.0',
          'publicsuffixlist >= 0.6.1',
          'six >= 1.11.0',
          'unittest2 >= 1.1.0',
          'future >= 0.16.0',
      ],
      )
