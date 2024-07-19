#=========================== perceiver.reports.drafts ==========================
"""!

@brief    API for (text) serializing an activity report.

Drafts are classes that generate output from the given input signal, which is
sent through the reporting channel.
The most basic version of a draft class would be plain text outout, but we can
envision other versions like JSON or csv compliant outputs.  Any data storage scheme
is valid as long as it permits some form of sequential outputting and does not require
backtracking.

@author   Patricio A. Vela,     pvela@gatech.edu 
@date     2024/05/23            [created]

"""
#=========================== perceiver.reports.drafts ==========================
#!
#!NOTE:
#!  set indent to 2 spaces.
#!  do not indent function code.
#!  set tab to 4 spaces with conversion to spaces.
#!  90 columns, word margin 9 or 10. 
#
#=========================== perceiver.reports.drafts ==========================

from ivapy.Configuration import AlgConfig


#================================= Announcement ================================
#

class CfgAnnouncement(AlgConfig):
  """!
  @ingroup  Reports
  @brief    Configuration instance for an Announcement.

  """

  #------------------------------ __init__ -----------------------------
  #
  def __init__(self, init_dict=None, key_list=None, new_allowed=True):
    '''!
    @brief    Instantiate a channel build configuration.
    '''

    if init_dict is None:
      init_dict = CfgAnnouncement.get_default_settings()

    super(CfgAnnouncement,self).__init__(init_dict, key_list, new_allowed)


  #------------------------ get_default_settings -----------------------
  #
  @staticmethod
  def get_default_settings():
    """!
    @brief  Get default build configuration settings for Trigger.
    """

    default_settings = dict(signal2text = None)
    return default_settings



class Announcement:
  """!
  @ingroup  Reports
  @brief    Base/abstract announcer class.

  An announcement packages a signal into text for reporting purposes.  The python
  logging API does not really have an analog to this because a logger is given the
  text to output.  Here, the signal is given and it must be converted to text.
  The conversion may require specific formatting needs to render it interpretable by a
  follow-up post-processing routine, or it might even not be text.  An overloaded
  announcer may package it up differently for the channel to output, based on the
  channel design (it may serialize data provided in a specific format as in the case
  of ROS messages).

  The base announcer relies on function pointers that perform signal translation.
  """

  #============================== Channel __init__ =============================
  #
  def __init__(self, theConfig):
    """!
    @brief  Constructor for announcer class.
    """
    self.config = theConfig
    self.announcement = None

  #================================== prepare ==================================
  #
  def prepare(self, theSignal):
    """!
    @brief  Prepare the announcement (e.g., convert to text for reporting out).

    @param[in]  theSignal   The signal attached to the announcement.
    """
    self.announcement = self.config.signal2text(theSignal)

  #================================== message ==================================
  #
  def message(self):
    """!
    @brief  Return the announcement message. 
    """
    return self.announcement

  #==================================== ack ====================================
  #
  def ack(self):
    """!
    @brief  Send along to Announcement that Channel acknowledges message.

    Acknowledgement simply lets the Channel know that there was an action that took
    place.  The channel may not need to know anything about that, in which case
    the ack can be ignored.  However, if internal state information requires knowing
    when the Channel has acted, then this can be useful to reset internal states.
    """
    pass



  #========================= signal2text static methods ========================
  #

  @staticmethod
  def passthrough(fsig):
    return fsig

  @staticmethod
  def toiterable(fsig):
    if fsig is None:
      return None
    else:
      return [fsig]

  @staticmethod
  def alwaystoiterable(fsig):
    return [fsig]

  @staticmethod
  def float2text(fspec = "{}"):
    """!
    @brief  Convert float to string based on preset specification.

    @param[in]  fspec   The given specification.

    @return     Returns a function pointer that convert float to string.
    """
    def inF2T(fsig):
      return fspec.format(fsig)

    return inF2T



  @staticmethod
  def int2text(isig):
    """!
    @brief  Convert integer to string.

    @param[in]  isig   The integer.

    @return     Returns integer as a string. 
    """
    return str(isig)

  @staticmethod
  def text2text(ssig):
    """!
    @brief  Signal is already a string, so just return. (Should be rare)

    @param[in]  ssig   The string.

    @return     Returns same string. 
    """
    return ssig

  @staticmethod
  def counter(icnt = 0, cspec = "{}"):
    """!
    @brief  Signal is ignored and replace with invocation counter.

    Every time the trigger happens to involve counter, the counter increases.
    It starts with 0.  If something else should be used, then pass in the
    initial value when creating the pointer.

    @return     Counter value.
    """

    def cntFun(igsig=None):
      nonlocal icnt
      rcnt = icnt
      icnt = icnt + 1
      return cspec.format(rcnt)

    return cntFun

  @staticmethod
  def counterWithReset(icnt = 0, cspec = "{}"):
    """!
    @brief  Signal is ignored and replace with invocation counter.

    Every time the trigger happens to involve counter, the counter increases.
    It starts with 0.  If something else should be used, then pass in the
    initial value when creating the pointer.

    @return     Counter value.
    """
    tcnt = icnt

    def cntFun(igsig=None):
      nonlocal tcnt
      rcnt = tcnt
      tcnt = tcnt + 1
      return cspec.format(rcnt)

    def rstFun(igsig=None):
      nonlocal tcnt
      nonlocal icnt
      tcnt = icnt
      return ""

    return [cntFun, rstFun]


  @staticmethod
  def fixed(theAnnouncement):
    """!
    @brief  Signal is ignored and replace with a fixed output.

    Rather than use the signal to generate the message, a fixed announcement
    is output. The fixed announcement should be provided when generating the
    function pointer.

    @return     The fixed announcement.
    """

    def fixedFun(igsig=None):
      return theAnnouncement

    return fixedFun

  @staticmethod
  def timeof():
    """!
    @brief  Signal is ignored and replace with current time (as string).

    Rather than use the signal to generate the message, use the time of the signal
    occurence to be the announcement. 

    @return     The fixed announcement.
    """
    from datetime import datetime

    def fixedFun(igsig=None):
      now = datetime.now()
      return str(now.time())

    return fixedFun


#================================== Commentary =================================
#

class CfgCommentary(CfgAnnouncement):
  """!
  @ingroup  Reports
  @brief    Configuration instance for Commentary.

  """

  #------------------------------ __init__ -----------------------------
  #
  def __init__(self, init_dict=None, key_list=None, new_allowed=True):
    '''!
    @brief    Instantiate a channel build configuration.
    '''

    if init_dict is None:
      init_dict = CfgCommentary.get_default_settings()

    super(CfgCommentary,self).__init__(init_dict, key_list, new_allowed)


  #------------------------ get_default_settings -----------------------
  #
  @staticmethod
  def get_default_settings():
    """!
    @brief  Get default build configuration settings for Trigger.
    """

    default_settings = CfgAnnouncement.get_default_settings()
    default_settings.update(dict(signalsaver = None))

    return default_settings


class Commentary(Announcement):
  """!
  @ingroup  Reports
  @brief    Commentary class, which does not transcribe the signal but passes it
            along in some non-text format.

  A commentary repackages a signal for passing it along.  Unlike an announcement,
  the commentary may or may not be immediately converted to text and output via a
  channel.  Rather it exists in storage until ready for use.  The expected
  implementation is that some external source will request the information rather
  than being passed along automatically.  

  Consequently, static signal saving methods are also needed that do not convert the
  signal to text but rather return what part of the signal to save.  In most cases, a
  passthrough (inherited from Announcement) will do.  However, there are some cases
  where the triggered signal is used to create a different kind of message. Downstream
  processing may prefer to get the commentary rather than convert it into a
  text/string announcement.  It is up to the downstream part to establish approach.

  The design makes sense when used with a BeatReporter who would pass the data along
  to an Editor.  The Editor can sit on the data, or elect to publish it through the
  Editor's Channel. If the Channel can process binary or non-text data, then using
  the Commentary would be the sensible outcome.
  """

  #============================== Channel __init__ =============================
  #
  def __init__(self, theConfig):
    """!
    @brief  Constructor for Commentary class.
    """
    self.config = theConfig
    self.announcement = None
    self.commentary   = None

  #================================== prepare ==================================
  #
  def prepare(self, theSignal):
    self.commentary = self.config.signalsaver(theSignal)

  #================================= reportout =================================
  #
  def reportout(self):
    if (self.config.signal2text is None):
      self.announcement = ""
    else:
      self.announcement = self.config.signal2text(self.commentary)

  #================================== message ==================================
  #
  def message(self):
    """!
    @brief  Return the commentary message. 
    """
    if (self.config.signal2text is None):
      return self.commentary
    else:
      return self.config.signal2text(self.commentary)


  #========================= signalsaver static methods ========================
  #
  #
  @staticmethod
  def counter(icnt = 0, cspec = "{}"):
    """!
    @brief  Signal is ignored and replace with invocation counter.

    Every time the trigger happens to involve counter, the counter increases.
    It starts with 0.  If something else should be used, then pass in the
    initial value when creating the pointer.

    @return     Counter value.
    """

    def cntFun(igsig=None):
      nonlocal icnt
      rcnt = icnt
      icnt = icnt + 1
      return rcnt

    return cntFun

  @staticmethod
  def timeof():
    """!
    @brief  Signal is ignored and replace with current time in raw/time format.

    Rather than use the signal to generate the message, use the time of the signal
    occurence to be the announcement. 

    @return     The fixed announcement.
    """
    from datetime import datetime

    def fixedFun(igsig=None):
      now = datetime.now()
      return now.time()

    return fixedFun

#============================== RunningCommentary ==============================
#

class CfgRunningCommentary(CfgAnnouncement):
  """!
  @ingroup  Reports
  @brief    Configuration instance for RunningCommentary.

  """

  #------------------------------ __init__ -----------------------------
  #
  def __init__(self, init_dict=None, key_list=None, new_allowed=True):
    '''!
    @brief    Instantiate a channel build configuration.
    '''

    if init_dict is None:
      init_dict = CfgRunningCommentary.get_default_settings()

    super(CfgRunningCommentary,self).__init__(init_dict, key_list, new_allowed)



  #------------------------ get_default_settings -----------------------
  #
  @staticmethod
  def get_default_settings():
    """!
    @brief  Get default build configuration settings for Trigger.
    """

    default_settings = CfgCommentary.get_default_settings()

    return default_settings



class RunningCommentary(Commentary):
  """!
  @ingroup  Reports
  @brief    Commentary class that also keeps track of past information and reports
            it all out when requested. At that point, it should wipe the past
            information and start collecting anew.

  The commentary will either be directly access for use, or it will be reported
  out.  Reporting out does conversion to text.
  """

  #============================== Channel __init__ =============================
  #
  def __init__(self, theConfig):
    """!
    @brief  Constructor for RunningCommentary class.
    """
    super(RunningCommentary,self).__init__(theConfig);

    self.commentary = list()

  #================================== prepare ==================================
  #
  def prepare(self, theSignal):
    """!
    @brief  Prepare the commentary (e.g., convert to storage format).

    @param[in]  theSignal   The signal attached to the announcement.
    """
    self.commentary.append(self.config.signalsaver(theSignal))

  #==================================== ack ====================================
  #
  def ack(self):
    """!
    @brief  Send along to Announcement that Channel acknowledges message.

    For a RunningCommentary, acknowledgement indicates that the stored information
    was used or somehow passed on.  Thus, the old information should be removed
    so that new information may be accumulated.
    """
    self.commentary = list()


#
#=========================== perceiver.reports.drafts ==========================
