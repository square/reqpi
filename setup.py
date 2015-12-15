# Copyright (c) Square, Inc.
# See LICENSE for details.
import setuptools

import versioneer

with open('README.rst') as fp:
    long_description = fp.read()

setuptools.setup(
    url='https://github.com/square/reqpi',
    packages=setuptools.find_packages() + ['twisted.plugins'],
    install_requires=['mainland', 'Twisted'],
    name='reqpi',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    author='Square, Inc.',
    author_email='moshez@squareup.com',
    description='Requirements-only PyPI-compatible server',
    long_description=long_description,
    license='Apache',
)
