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
# runs the script.  The output is a CSV file whose contents are noted at the
# end of this document.
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
cfAnn.signal2text = Announce.Announcement.passthrough
cfCSV = Channdel.CfgToFile();
cfCSV.filename = "report04output.csv"

crier = Announce.Announcement(cfAnn)
media = Channel.toCSV(cfCSV)

testRep = Reports.Reporter(trigr, crier, media)
flist = (1.0, 2.0, 3.0, 3.2, 10.1, 20.5, 20.7, 50.2)

print("=== Always    : All flag values. ===")
for si in flist:
  testRep.process(si)

#
#================================ report04csv =================================
