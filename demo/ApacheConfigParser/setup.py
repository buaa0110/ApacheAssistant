"""Apache Configuration parser

See:
https://github.com/mikemrm/ApacheConfigParser
"""

from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='ApacheConfig',
    version='0.0.1.dev1',
    description='Apache Config Parser',
    long_description=long_description,
    url='https://github.com/mikemrm/ApacheConfigParser',
    author='Mike Mason',
    author_email='apacheconfigparser-github@mrm.one',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
    ],
    keywords='apache config parser',
    packages=find_packages(exclude=['re', 'shlex']),
    install_requires=[],
    entry_points={
        'console_scripts': [
            'parser=ApacheConfig:ApacheParser',
        ],
    },
)