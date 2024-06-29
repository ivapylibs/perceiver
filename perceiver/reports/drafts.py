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


  #========================= signal2text static methods ========================
  #

  @staticmethod
  def passthrough(fsig):
    return fsig

  @staticmethod
  def signal2iterable(fsig):
    return [fsig]


  @staticmethod
  def float2text(fspec):
    """!
    @brief  Convert float to string based on preset specification.

    @param[in]  fspec   The given specification.

    @return     Returns a function pointer that convert float to string.
    """

    return inF2T

    def inF2T(fsig):
      return fspec.format(fsig)


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

    super(CfgAnnouncement,self).__init__(init_dict, key_list, new_allowed)


  #------------------------ get_default_settings -----------------------
  #
  @staticmethod
  def get_default_settings():
    """!
    @brief  Get default build configuration settings for Trigger.
    """

    default_settings = CfgCommentary.get_default_settings()
    default.settings.update(dict(signalsaver = None))

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

  In that context, it makes sense when used with a BeatReporter who would pass the
  data along to an Editor.  The Editor can sit on the data, or elect to publish it
  through the Editor's Channel.
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
    self.announcement = self.config.signal2text(self.commentary)

#============================== RunningCommentary ==============================
#

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
    super(self).__init__(theConfig);

  #================================== prepare ==================================
  #
  def prepare(self, theSignal):
    """!
    @brief  Prepare the commentary (e.g., convert to storage format).

    @param[in]  theSignal   The signal attached to the announcement.
    """
    self.commentary = self.config.signalsaver(theSignal, self.commentary)

#
#=========================== perceiver.reports.drafts ==========================
