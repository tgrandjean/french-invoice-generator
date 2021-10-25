#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ["pydantic==1.8.2",
                "Jinja2==3.0.2",
                "email-validator==1.1.3"]

test_requirements = ['pytest>=3', ]

setup(
    author="Thibault Grandjean",
    author_email='thibault@cornet-grandjean.com',
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="generate french invoices with latex from python",
    install_requires=requirements,
    license="Apache Software License 2.0",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='invoice_generator',
    name='french-invoice-generator',
    packages=find_packages(include=['invoice_generator',
                                    'invoice_generator.*']),
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/tgrandjean/french-invoice-generator',
    version='0.3',
    zip_safe=False,
    package_data={'': ['templates/*']}
)
