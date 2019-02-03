#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='my_django_extension',
    version='1.0',
    description='Useful extensions for django',
    long_description=open('README.md').read(),
    author='aamishbaloch',
    url='https://github.com/aamishbaloch/my-django-extensions',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Django==2.1.5',
        'djangorestframework==3.9.1',
        'pytz==2018.9',
    ],
)
