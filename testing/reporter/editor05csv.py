#!/usr/bin/python3
#================================= editor05sv =================================
## @file
# @brief    Code to test editor scheme with Commentary instances under hard coded loop.
# 
# Builds on ``editor01simple`` by replacing the Announcements with Commentary, such
# that the Commentary instances have no signal2text function pointer (set to None).
# In doing so, the Commentary instance is implicitly told to pass along the
# internal commentary as the message.  The commentary can be binary data and not
# necessarily printable.  
#
# In this case, the outputs are indeed printable and the output should be similar
# to ``editor01simple`` but in a CSV file and with some timing information.
#
# The code below
# 
# > ./editor05sv.py
# 
# runs the script.  The output is text trial number and timing information.
# The running times are pre-specified floats, while the trial termination
# time does us actual timing.   
#
# @ingroup  TestReporter
# @quitf
#
# @author   Patricio A. Vela,   pvela@gatech.edu
# @date     2024/06/28 [created]
#
#================================= editor05sv =================================
#
#NOTE:
#  Number of columns is 90 with margin at 10.
#  Indent is set to 2 spaces.
#  Tab is set to 4 spaces with conversion to spaces.
#
#================================= editor05sv =================================

#==[0] Environment setup.
#
import time
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
trigs = [Trigger.Falling(), Trigger.Rising(), Trigger.Always()]

# BeatReporters all have same Announcement but send different 
# text to it, possibly even None (a skip/do nothing).
# The Commentary outputs it according to its text output scheme.
# In this case, it should be a printf equivalent.
# Also, all of the BeatReporters lead to "output" outcomes.
#
bquiet  = [False, True, True]
sigfilt = [Announce.Commentary.timeof(), Announce.Commentary.counter(), None ]

bReporters = Reports.BeatReporter.buildGroupWithRunningCommentary(
                triggers = trigs, keepQuiet = bquiet, filters = sigfilt)


trigs   = [Trigger.Rising(), Trigger.onMatch(None, True), Trigger.Falling()]
bquiet  = [True, True, False]
sigfilt = [Announce.Announcement.fixed("-")] + Announce.Commentary.counterWithReset()

bReporters2 = Reports.BeatReporter.buildGroupWithRunningCommentary(
                triggers = trigs, keepQuiet = bquiet, filters = sigfilt)

bReporters.extend(bReporters2)

#==[2] Editor configuration.

# The Editor will need an output channel.
cfChan = Channel.CfgToFile();
cfChan.filename = "editor05output.csv"
media  = Channel.toCSV(cfChan)

tEditor  = Reports.Editor(media)
tEditor.assignGroup(bReporters)  


print("=== Output to text. Two rows per outer loop, with \"timings\" ==")
# The BeatReporters will pass along to Editor who will output when appropriate.

flist = (0.0, 1.0, 2.2, 2.5, 5.7, 6.2)
for ni in range(3):
  #send False to binary BeatReporters
  bReporters[0].process(False)
  bReporters[1].process(False)

  bReporters[3].process(False)
  bReporters[4].process(False)
  bReporters[5].process(False)

  for si in flist:
    #send number to numerical BeatReporter
    bReporters[0].process(True)
    bReporters[1].process(True)
    bReporters[2].process(si)       # Comes from flist.

    bReporters[3].process(True)     # Should record puzzle piece counts.
    bReporters[4].process(True)
    bReporters[5].process(True)

  time.sleep(0.25)

bReporters[0].process(False)
bReporters[1].process(False)
bReporters[3].process(False)
bReporters[4].process(False)
bReporters[5].process(False)



# EXPECTED OUTPUT, EXCEPT THAT LAST ENTRY IN SECONDS SHOULD REFLECT 
# CURRENT TIME AT INVOCATION OF SCRIPT:
#
# 0,0.0,1.0,2.2,2.5,5.7,6.2,18:29:24.248032
# -,0,1,2,3,4,5,
# 1,0.0,1.0,2.2,2.5,5.7,6.2,18:29:24.498512
# -,0,1,2,3,4,5,
# 2,0.0,1.0,2.2,2.5,5.7,6.2,18:29:24.748955
# -,0,1,2,3,4,5,
#
#
#================================= editor05sv =================================
