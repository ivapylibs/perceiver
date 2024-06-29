#!/usr/bin/python3
#================================ report03float ================================
## @file
# @brief    Code to test out the reporter functionality under hard coded loop.
# 
# A few basic trigger types for flag/binary type signals are tested here.
# 
# The code below
# 
# > ./report03float
# 
# runs the script.  It tests out the Always, whenClose, whenFar, whenDiffers,
# whenSimilar triggers.
# 
# @ingroup  TestReporter
# @quitf
#
# @author   Patricio A. Vela,   pvela@gatech.edu
#
# @date     2024/05/30 [created]
#
#================================ report03float ================================
#
#NOTE:
#  Number of columns is 90 with margin at 10.
#  Indent is set to 2 spaces.
#  Tab is set to 4 spaces with conversion to spaces.
#
#================================ report03float ================================

import perceiver as perceiver
 
import perceiver.reports.drafts   as Announce
import perceiver.reports.triggers as Triggers
import perceiver.reports.channels as Channel
import perceiver.reporting        as Reports

import math


trigr = Triggers.Always()

cfAnn = Announce.CfgAnnouncement()
cfAnn.signal2text = Announce.Announcement.int2text
print(cfAnn.signal2text)

crier = Announce.Announcement(cfAnn)
media = Channel.Channel()

testRep = Reports.Reporter(trigr, crier, media)
flist = (1.0, 2.0, 3.0, 3.2, 10.1, 20.5, 20.7, 50.2)

print("=== Always    : All flag values. ===")
for si in flist:
  testRep.process(si)


cfgClose = Triggers.CfgDistTrigger(None)
cfgClose.tau = 5
cfgClose.distance = Triggers.CfgDistTrigger.scalarDist

trigr = Triggers.whenClose(cfgClose, 2)
testRep = Reports.Reporter(trigr, crier, media)

print("=== When Close : Close  4 times.  ===")
for si in flist:
  testRep.process(si)

trigr = Triggers.whenFar(cfgClose, 2)
testRep = Reports.Reporter(trigr, crier, media)

print("=== When Far   : Far    4 times.  ===")
for si in flist:
  testRep.process(si)

trigr = Triggers.whenDiffers(cfgClose, 2)
testRep = Reports.Reporter(trigr, crier, media)

print("=== When Differs : Differs 3 times.  ===")
for si in flist:
  testRep.process(si)

trigr = Triggers.whenSimilar(cfgClose, 2)
testRep = Reports.Reporter(trigr, crier, media)

print("=== When Similar : Similar 4 times.  ===")
for si in flist:
  testRep.process(si)
