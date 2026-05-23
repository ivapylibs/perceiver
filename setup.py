#
#! NOTE:    90 columns wide.
#!
#

from setuptools import setup, find_packages


setup(
    name="perceiver",
    version="1.0.1",
    description="Classes implementing detection based processing pipelines.",
    author="IVALab",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "matplotlib",
    ],
)
