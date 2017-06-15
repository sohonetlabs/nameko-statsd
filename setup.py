#!/usr/bin/env python
from setuptools import setup


def reqs(filepath):
    with open(filepath) as stream:
        return [line.strip() for line in stream.readlines()]


setup(
    name='nameko-statsd',
    version='0.0.2',
    description='StatsD dependency for nameko services',
    author='Sohonet product team',
    author_email='fabrizio.romano@sohonet.com',
    url='https://github.com/sohonetlabs/nameko-statsd',
    packages=['nameko_statsd'],
    install_requires=reqs('requirements/base.txt'),
    extras_require={
        'dev': reqs('requirements/dev.txt'),
    },
    zip_safe=True,
    license='MIT',
    classifiers=[
        "Programming Language :: Python",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Intended Audience :: Developers",
    ]
)
