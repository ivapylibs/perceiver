#!/usr/bin/env/python
"""!
@defgroup   Perceiver Perceiver

@brief  Perception code that aims to extract interpretable signals from a visual
        stream.

The most basic perceiver consists of a detector and a tracker, and returns some vector
quantity related to a detected instance in the image.  Adding a track filter will, in
principle, provide a cleaner output signal less affected by noise or measurement
uncertainty.  More complex implementations follow.

Sometimes the tracked signals are not important, but rather their meaning.  In that
case an activity/action detector or recognizer will convert the tracked signal(s)
into semantically meaningful labels or their equivalent. A Monitor packages these two
together.

Likewise, there may be a need to compare the perceived state to some target or goal
state.  The most common reason for this comparison would be to assess completion or
proximity to the target/goal state. In that case a Progress monitor is needed.

This package attempts to encapsulate the generic functionality of these different
classes (Perceiver, Monitor, Progress monitor).


"""
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
