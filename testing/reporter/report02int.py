#!/usr/bin/python3
#================================= report01flag ================================
## @file
# @brief    Code to test out the reporter functionality under hard coded loop.
# 
# A few basic trigger types for flag/binary type signals are tested here.
# 
# The code below
# 
# > ./report02int
# 
# runs the script.  It tests out the Always, onChange, onMatch, whenClose, whenFar,
# whenDiffers, whenSimilar triggers.
# 
# @ingroup  TestReporter
# @quitf
#
# @author   Patricio A. Vela,   pvela@gatech.edu
#
# @date     2024/05/30 [created]
#
#================================= report01flag ================================
#
#NOTE:
#  Number of columns is 90 with margin at 10.
#  Indent is set to 2 spaces.
#  Tab is set to 4 spaces with conversion to spaces.
#
#================================= report01flag ================================

import perceiver as perceiver

import perceiver.reports.drafts   as Announce
import perceiver.reports.triggers as Triggers
import perceiver.reports.channels as Channel
import perceiver.reporting        as Reports

import types


trigr = Triggers.Always()

cfAnn = Announce.CfgAnnouncement()
cfAnn.signal2text = Announce.Announcement.int2text
print(cfAnn.signal2text)

crier = Announce.Announcement(cfAnn)
media = Channel.Channel()

testRep = Reports.Reporter(trigr, crier, media)
flist = (1, 2, 3, 3, 10, 20, 20, 50)

print("=== Always    : All flag values. ===")
for si in flist:
  testRep.process(si)


trigr = Triggers.onChange()
testRep = Reports.Reporter(trigr, crier, media)

print("=== On Change : Switch 5 times.  ===")
for si in flist:
  testRep.process(si)

trigr = Triggers.onMatch(None, 3)
testRep = Reports.Reporter(trigr, crier, media)

print("=== On Match  : Match  2 times.  ===")
for si in flist:
  testRep.process(si)

trigr = Triggers.onMatch(None, 10)
testRep = Reports.Reporter(trigr, crier, media)

print("=== On Match  : Match  1 times.  ===")
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
