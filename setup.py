"""Analog - Log Analysis Utitliy."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from setuptools import setup, find_packages


VERSION = '0.1.7'


def read(path, strip=False):
    """Read file at ``path`` and return content. Opt., ``strip`` whitespace."""
    content = ''
    with open(path) as fp:
        content = fp.read()
        if strip:
            content = content.strip()
    return content


classifiers = [
    'Development Status :: 3 - Alpha',
    'Environment :: Console',
    'Intended Audience :: Developers',
    'Intended Audience :: System Administrators',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Programming Language :: Python :: 3',
    'Topic :: Internet :: Log Analysis',
    'Topic :: System :: Logging',
    'Topic :: System :: Monitoring',
    'Topic :: System :: Systems Administration',
    'Topic :: Utilities',
    'Programming Language :: Python :: 3'] + [
    'Programming Language :: Python :: {0}'.format(pyv)
    for pyv in "2.7 3.3".split()
]


requirements = ['tabulate']
# unittest.mock (3.3+) or mock
try:
    import unittest.mock
    del unittest.mock
except ImportError:
    requirements.append('mock')
# configparser available? (3+)
try:
    import configparser
    del configparser
except ImportError:
    requirements.append('configparser')


setup(
    name='analog',
    description='analog - Log Analysis Utility',
    long_description=read('README.rst') + '\n\n' + read('CHANGELOG.rst'),
    version=VERSION,
    url='https://bitbucket.org/fabianbuechler/analog',
    license='MIT license',
    author='Fabian B\xfcchler',
    author_email='fabian.buechler@gmail.com',
    entry_points={'console_scripts': ['analog=analog:main']},
    classifiers=classifiers,
    install_requires=requirements,
    packages=find_packages(),
    py_modules=['analog'],
    zip_safe=False,
)
