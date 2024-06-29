#!/usr/bin/python3
#================================= report01flag ================================
## @file
# @brief    Code to test out the reporter functionality under hard coded loop.
# 
# A few basic trigger types for flag/binary type signals are tested here.
# 
# The code below
# 
# > ./report01flag
# 
# runs the script.  It tests out the Always, onChange, and onMatch triggers.
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


trigr = Triggers.Trigger()

cfAnn = Announce.CfgAnnouncement()
cfAnn.signal2text = Announce.Announcement.int2text
print(cfAnn.signal2text)

crier = Announce.Announcement(cfAnn)
media = Channel.Channel()

testRep = Reports.Reporter(trigr, crier, media)
flist = (False, True, True, True, True, False)

print("=== Trigger   : Never triggers.  ===")
for si in flist:
  testRep.process(si)


trigr = Triggers.Always()
testRep = Reports.Reporter(trigr, crier, media)

print("=== Always    : All flag values. ===")
for si in flist:
  testRep.process(si)


trigr = Triggers.onChange()
testRep = Reports.Reporter(trigr, crier, media)

print("=== On Change : Switch 2 times.  ===")
for si in flist:
  testRep.process(si)

trigr = Triggers.onMatch(None, False)
testRep = Reports.Reporter(trigr, crier, media)

print("=== On Match  : False  2 times.  ===")
for si in flist:
  testRep.process(si)

trigr = Triggers.onMatch(None, True)
testRep = Reports.Reporter(trigr, crier, media)

print("=== On Match  : True   4 times.  ===")
for si in flist:
  testRep.process(si)
