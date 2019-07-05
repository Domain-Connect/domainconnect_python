#!/usr/bin/env python

from setuptools import setup

setup(name='domain_connect',
      version='0.0.6',
      description='Python client library for Domain Connect protocol. See: https://domainconnect.org',
      long_description_content_type="text/markdown",
      long_description=open('README.md').read(),
      author='Pawel Kowalik',
      author_email='pawel-kow@users.noreply.github.com',
      url='https://github.com/Domain-Connect/domainconnect_python',
      license='https://github.com/Domain-Connect/domainconnect_python/blob/master/LICENSE',
      classifiers=[
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.6',
      ],
      packages=[
          'domainconnect',
      ],
      install_requires=[
          'dnspython >= 1.15.0',
          'publicsuffix >= 1.1.0',
          'publicsuffixlist >= 0.6.1',
          'six >= 1.11.0',
          'future >= 0.16.0',
          'cryptography >= 2.7'
      ],
      )
