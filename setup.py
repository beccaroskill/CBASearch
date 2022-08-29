#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages


with open('README.md') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['uvicorn==0.18.3',
                'pandas==1.4.2',
                'fastapi==0.81.0',
                'Whoosh==2.7.4',
                'python-multipart==0.0.5',
                'Jinja2>=2.11.2',
                'Whoosh==2.7.4']

test_requirements = [ ]

setup(
    author="Becca Roskill",
    author_email='beccaroskill@gmail.com',
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="Search Collective Bargaining Agreements made available by the Department of Labor.",
    entry_points={
        'console_scripts': [
            'cba_search=cba_search.cli:main',
        ],
    },
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='cba_search',
    name='cba_search',
    packages=find_packages(include=['cba_search', 'cba_search.*']),
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/beccaroskill/cba_search',
    version='0.1.2.3',
    zip_safe=False,
)
