#!/usr/bin/python3
#================================ report04csv =================================
## @file
# @brief    Code to test reporter with csv output under hard coded loop.
# 
# Always triggers.  Just need to check that CSV output is proper.  Here the
# announcement is a pass through since CSV writer will do the "serialization."
# 
# The code below
# 
# > ./report04csv
# 
# runs the script.  The output is a CSV file whose contents are the floats
# packaged into a list within the code.
# 
# @ingroup  TestReporter
# @quitf
#
# @author   Patricio A. Vela,   pvela@gatech.edu
# @date     2024/06/28 [created]
#
#================================ report04csv =================================
#
#NOTE:
#  Number of columns is 90 with margin at 10.
#  Indent is set to 2 spaces.
#  Tab is set to 4 spaces with conversion to spaces.
#
#================================ report04csv =================================

import perceiver as perceiver

import perceiver.reports.drafts   as Announce
import perceiver.reports.triggers as Triggers
import perceiver.reports.channels as Channel
import perceiver.reporting        as Reports

import math

trigr = Triggers.Always()

cfAnn = Announce.CfgAnnouncement()
cfAnn.signal2text = Announce.Announcement.toiterable
cfCSV = Channel.CfgToFile();
cfCSV.filename = "report05output.csv"

crier = Announce.Announcement(cfAnn)
media = Channel.toCSV(cfCSV)

testRep = Reports.Reporter(trigr, crier, media)
flist = (1.0, 3.0, 3.2, 20.5, 20.7, 50.2)

print("=== No output, goes to CSV file.  Check it against text output. ==")
media.sendHeader(["Iteration", "Times"])
ni = 0
for si in flist:
  media.setRunner(ni)
  testRep.process(si)
  ni = ni+1

#
#================================ report04csv =================================
