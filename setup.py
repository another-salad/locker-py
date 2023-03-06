"""Setup"""

import os
from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="lockerpy",
    author="Jumbo Bumbo",
    long_description=read('README.md'),
    license="BSD",
    python_requires='>=3.9',
    packages=find_packages(),
    install_requires=read("requirements.txt"),
    entry_points=dict(
        console_scripts=[
            'generate = src.locker.console:generate'
        ]
    ),
    include_package_data=True
)
