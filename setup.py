__author__ = 'markj'

from setuptools import setup

setup(
    name="binary to nar",
    version="0.0.1-SNAPSHOT",
    packages={"binToNar"},
    #py_modules=['binToNar'],
    install_requires=[
        "Click",
        "colorama"
    ],
    entry_points="""
        [console_scripts]
        binToNar=binToNar.binToNar:enterCommandLine
    """,
)
