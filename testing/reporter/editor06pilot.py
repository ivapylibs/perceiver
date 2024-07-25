#!/usr/bin/python3
#================================ editor06pilot ================================
## @file
# @brief    Code that generates an test editor scheme compatible with the UCF
#           puzzle placing pilot study.
# 
# This script builds on ``editor05csv`` and creates output more inline with what
# the UCF Pilot Study 01 should be generating.  The differences involve
# prettying up with header and related content. Possibly also adding output
# involving the puzzle board area and puzzle solution area, which can be used
# to test out puzzle completion, or if a puzzle piece was moved but not actually
# fit into the puzzle (the presumption here being that it gets left somewhere
# that would not affect the puzzle solution area.  
#
# TODO: Last sentence above should be confirmed.
#
# The code below
# 
# > ./editor06pilot.py
# 
# runs the script.  
#
# The output is text trial number, puzzle pieces, and timing information.
# The running times are pre-specified floats, while the trial termination
# time does us actual timing.   
#
# TODO: revise above when script is done.
#
# @ingroup  TestReporter
# @quitf
#
# @author   Patricio A. Vela,   pvela@gatech.edu
# @date     2024/06/28 [created]
#
#================================ editor06pilot ================================
#
# NOTE:
#  Number of columns is 90 with margin at 10.
#  Indent is set to 2 spaces.
#  Tab is set to 4 spaces with conversion to spaces.
#
#================================ editor06pilot ================================

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
#
# A set of BeatReporters will all have same Announcement but send different 
# text to it, possibly even None (a skip/do nothing).
# The Running Commentary output is according to its text output scheme.
#

# The first set of Beat Reporters is for outputting trial information
# Rising is start of trial.  Gets binary signal concerning solution board.
#
trigs   = [Trigger.Rising(initState = False), Trigger.Rising(initState = False)]
bquiet  = [True, False]
sigfilt = [Announce.Commentary.counter(icnt = 1), Announce.Announcement.dateof()]

theConfig = Announce.CfgRunningCommentary()
theConfig.Leader = 'Trial'

trialReport = Reports.BeatReporter.buildGroupWithRunningCommentary(
                triggers = trigs, keepQuiet = bquiet, filters = sigfilt,
                commentCfg = theConfig)

# The second set of Beat Reporters is for outputting puzzle piece information.
# In particular, when subject has indicated placement of a piece.
#
trigs   = [Trigger.Rising(initState=False), Trigger.onMatch(None, True), 
           Trigger.Falling(initState=False)]
bquiet  = [True, True, False]
sigfilt = [Announce.Announcement.fixed("-")] + Announce.Commentary.counterWithReset()

theConfig = Announce.CfgRunningCommentary()
theConfig.Leader = 'Piece'

pieceReport = Reports.BeatReporter.buildGroupWithRunningCommentary(
                triggers = trigs, keepQuiet = bquiet, filters = sigfilt,
                commentCfg = theConfig)

# The third set of Beat Reporters is for outputting timing information.
#
trigs   = [Trigger.Falling(initState=False), Trigger.Rising(initState=False), 
           Trigger.Always()]
bquiet  = [False, True, True]
sigfilt = [Announce.Commentary.timeof(), Announce.Commentary.timeof(), None ]

theConfig = Announce.CfgRunningCommentary()
theConfig.Leader = 'Time'

timeReport = Reports.BeatReporter.buildGroupWithRunningCommentary(
                triggers = trigs, keepQuiet = bquiet, filters = sigfilt,
                commentCfg = theConfig)

bReporters = trialReport + pieceReport + timeReport

#==[2] Editor configuration.

# The Editor will need an output channel.
cfChan = Channel.CfgToFile();
cfChan.filename = "editor06output.csv"
cfChan.header   = ["Cluster Order: 12345", "Piece Order: Ascending"]
media  = Channel.toCSV(cfChan)

tEditor  = Reports.Editor(media)
tEditor.assignGroup(bReporters)  

media.sendHeader()

print("=== Output to text. Two rows per outer loop, with \"timings\" ==")
# The BeatReporters will pass along to Editor who will output when appropriate.

flist = (1.0, 1.5, 2.2, 2.5, 5.7, 6.2)

for ni in range(3):
  # Puzzle solution board is in place.
  bReporters[0].process(True)
  bReporters[1].process(True)

  for si in flist:
    # Puzzle place button pressed.
    #
    bReporters[2].process(True)     # Should record puzzle piece counts.
    bReporters[3].process(True)
    bReporters[4].process(True)

    bReporters[5].process(True)
    bReporters[6].process(True)
    bReporters[7].process(si)       # Comes from flist.

  time.sleep(0.25)

  # Puzzle solution board removed.
  #
  bReporters[0].process(False)
  bReporters[1].process(False)

  bReporters[2].process(False)
  bReporters[3].process(False)
  bReporters[4].process(False)

  bReporters[5].process(False)
  bReporters[6].process(False)


# Missing the Pilot study puzzle piece area counts.  Will add in actual version
# since it is a bit more effort than desired to "simulation" those parts.  The
# report outs are getting more complicated and hiding the trigger sources.
# The best next step is to actually integrate into the Monitor, as the next
# critical unknown is how to code up the signal passing from the Perceiver
# pipeline to the Reporting pipeline.


# EXPECTED OUTPUT, EXCEPT THAT LAST ENTRY IN SECONDS SHOULD REFLECT 
# CURRENT TIME AT INVOCATION OF SCRIPT:
#
# Cluster Order: 12345,Piece Order: Ascending
# Trial,1,2024-07-25
# Piece,-,0,1,2,3,4,5,
# Time,12:27:59.932468,1.0,1.5,2.2,2.5,5.7,6.2,12:28:00.182900
# Trial,2,2024-07-25
# Piece,-,0,1,2,3,4,5,
# Time,12:28:00.183091,1.0,1.5,2.2,2.5,5.7,6.2,12:28:00.433596
# Trial,3,2024-07-25
# Piece,-,0,1,2,3,4,5,
# Time,12:28:00.433678,1.0,1.5,2.2,2.5,5.7,6.2,12:28:00.684130
#
# Except that date and time fields should reflect data and time at invocation.
#
#================================ editor06pilot ================================
