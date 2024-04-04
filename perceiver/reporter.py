#============================== perceiver.reporter =============================
"""!

@brief    API for reporting outcomes of a perceived scene.

A Reporter takes perceiver, monitor, or progress output and reports on its meaning
in some kind of interpretable or standardized stream for interpretation by a human
or by a program.  Having this API permits different reporting mechanisms for the
same computer vision scheme.  Should it be triggered? Should it be CSV output for
Excel processing? Something else for other programs (python or Matlab)?

@author   Patricio A. Vela,     pvela@gatech.edu 
@date     2024/02/24            [created]
"""
#============================== perceiver.reporter =============================
#!
#!NOTE:
#!  set indent to 2 spaces.
#!  do not indent function code.
#!  set tab to 4 spaces with conversion to spaces.
#!  90 columns 
#
#============================== perceiver.reporter =============================

from ivapy.Configuration import AlgConfig


#=============================== BuildCfgReporter ==============================
#

class BuildCfgReporter(AlgConfig):
  """!
  @ingroup  Reporter
  @brief    Configuration instance for a Reporter.

  Instantiating a reporter usually requires a trigger and an announcer.  The
  trigger uses history of the state to report, or possible other externally
  derived states, to estalish when to "announce" a given piece of information.
  The announcer then pipes the message or announcement to the proper channel.

  All of the core implementations are overloadable through derived classes.
  Some generic versions are available.
  """

  #------------------------------ __init__ -----------------------------
  #
  def __init__(self, init_dict=None, key_list=None, new_allowed=True):
    '''!
    @brief    Instantiate a puzzle scene (black mat) detector.
    '''

    if init_dict is None:
      init_dict = CfgReporter.get_default_settings()

    super(CfgReporter,self).__init__(init_dict, key_list, new_allowed)


  #------------------------ get_default_settings -----------------------
  #
  @staticmethod
  def get_default_settings():
    """!
    @brief  Get default configuration settings for Perceiver.
    """

    default_settings = dict()
    return default_settings


#=================================== Reporter ==================================
#

class Reporter:
  """!
  @ingroup  Reporter
  @brief    Base/abstract reporter class.

  A reporter consists of a trigger and an announcer for a given state stream.  
  The trigger uses history of a state--or possible other externally derived 
  states--to estalish when to "announce" a given piece of information.
  The announcer then pipes the message or announcement to the proper channel.

  It is like a more flexible logging system with some of its structural elements.
  For example, the python logging API has loggers, handlers, filters, and formatters.
  Their analogs are reporters, handlers, triggers, and announcers. Based on intended use, a
  reporter is not the same as a logger.  First, the information given is not necessarily a
  string. Second, specific meta-data that normally gets output by the logger may not apply
  here and other meta-data may be of interest.  The caller will usually have created the
  reporter and use it as needed, as opposed to being generally used by all code.  Also, a
  logger is called when logging needed.  Here, a reporter gets called all the time with
  updated state information.  It decides (based on the trigger) when to report and how
  (based on the announcer).

  A reporter manages the higher level flow that goes from state information to output.
  This way programming can go from debug type outputs to highly structured output that
  supports analysis.  It can even be that the output is to a stream, thereby serving as
  input to some other process. Such a case could hold for ROS topic/message output types.
  """

  __init__

class RepStatus(Reporter):
  __init__


#
#============================== perceiver.reporter =============================
