#!/usr/bin/env python
from setuptools import setup


def reqs(filepath):
    with open(filepath) as stream:
        return [line.strip() for line in stream.readlines()]


description = 'StatsD dependency for nameko services.'


setup(
    name='nameko-statsd',
    version='0.1.3',
    description=description,
    long_description=description,
    long_description_content_type='text/x-rst',
    author='Sohonet product team',
    author_email='fabrizio.romano@sohonet.com',
    url='https://github.com/sohonetlabs/nameko-statsd',
    packages=['nameko_statsd'],
    install_requires=reqs('requirements/base.txt'),
    extras_require={
        'dev': reqs('requirements/dev.txt'),
    },
    zip_safe=True,
    license='MIT License',
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ]
)
