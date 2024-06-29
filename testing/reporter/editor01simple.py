#!/usr/bin/python3
#=============================== editor01simple ===============================
## @file
# @brief    Code to test editor scheme with text output under hard coded loop.
# 
# Designed to replicate the scheme needed for a puzzle placing timing test.
# There is a button trigger that the player presses.  There is a puzzle
# board flag that the tester influences for which falling and rising edge
# information has meaning (end of trial, start of trial).  These will feed
# different BeatReporter instances that collect time stamps and trial number.
# Gets output along the way.
#
# The code below
# 
# > ./editor01simple.py
# 
# runs the script.  The output is text trial number and timing information.
# There are some manual pauses to output more reasonable times.
# 
# @ingroup  TestReporter
# @quitf
#
# @author   Patricio A. Vela,   pvela@gatech.edu
# @date     2024/06/28 [created]
#
#=============================== editor01simple ===============================
#
#NOTE:
#  Number of columns is 90 with margin at 10.
#  Indent is set to 2 spaces.
#  Tab is set to 4 spaces with conversion to spaces.
#
#=============================== editor01simple ===============================

#==[0] Environment setup.
#
import perceiver as perceiver

import perceiver.reports.drafts   as Announce
import perceiver.reports.triggers as Trigger
import perceiver.reports.channels as Channel
import perceiver.reporting        as Reports

import math


#==[1] BeatReporters configurations.

# Triggers for float, boolean, boolean.  The float is trial
# data, the falling is the end of a trial, and the rising
# is the start of a trial.
#
trigs = [Trigger.Always(), Trigger.Falling(), Trigger.Rising()]

# BeatReporters all have same Announcement but send different 
# text to it, possibly even None (a skip/do nothing).
# The Commentary outputs it according to its text output scheme.
# In this case, it should be a printf equivalent.
# Also, all of the BeatReporters lead to "output" outcomes.
#
cfAnn = Announce.CfgAnnouncement()
cfAnn.signal2text = Announce.Announcement.CUSTOMIZE_PER_BR

# Assignments behave normally.  No need for custom build out.

#==[2] Editor configuration.

# The Editor will need an output channel.
cfChan = Channel.CfgChannel.forEditors();
media  = Channel.Channel(cfChan)

cfEditor = Reports.CfgEditor()  NEEDED
tEditor  = Reports.Editor(media)
tEditor.addBeats(theBeatReporters)  NEEDED


print("=== Output to text. One row per loop, with timings ==")
# The BeatReporters will pass along to Editor who will output when appropriate.

flist = (0.0, 1.0, 2.2, 2.5, 5.7, 6.2)
for ni in [0:2]:
  send False to binary BeatReporters

  for si in flist:
    send number to numerical BeatReporter

  send True to binary BeatReporters


DONE. SHOULD SEE OUTPUT. COPY BELOW FOR COMPARISON.


# EXPECTED OUTPUT:
#
#
#
#=============================== editor01simple ===============================
