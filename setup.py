#!/usr/bin/python
__author__ = 'Mark John Doyle'
__version__= '0.0a1'
__status__= 'Development'

from setuptools import setup 

setup(
    name="binary to nar",
    version="0.0a1",
    packages={"binToNar"},
    install_requires=[
        "Click",
        "colorama"
    ],
    entry_points="""
        [console_scripts]
        binToNar=binToNar.binToNar:enterCommandLine
    """,
)
