#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

setup_requirements = []
base_requirements = ['Click>=6.0', 'Faker']
api_requirements = ['tinydb', 'flask', 'flask_restful']
test_requirements = ['jsonschema', 'mock', 'tinydb', 'requests']

setup(
    author="John Giannelos",
    author_email='johngiannelos@gmail.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    description="Object generator based on IAM profile v2 schema",
    entry_points={
        'console_scripts': [
            'iam_profile_faker=iam_profile_faker.cli:main',
            'iam_profile_faker_api=iam_profile_faker.v2_api:main'
        ],
    },
    install_requires=base_requirements,
    extras_require={
        'api': api_requirements
    },
    license="Apache Software License 2.0",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='iam_profile_faker',
    name='iam_profile_faker',
    packages=find_packages(include=['iam_profile_faker']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/mozilla-iam/iam-profile-faker',
    version='0.3.0',
    zip_safe=False,
)
