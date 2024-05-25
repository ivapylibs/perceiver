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
        "Lie @ git+https://github.com/ivapylibs/Lie.git",
    ],
    extras_require={
        "testing": [
            "improcessor @ git+https://github.com/ivapylibs/improcessor.git",
            "detector @ git+https://github.com/ivapylibs/detector.git",
            "trackpointer @ git+https://github.com/ivapylibs/trackpointer.git",
        ]
    },
)
