#========================== perceiver.reports.channel ==========================
"""!

@author   Patricio A. Vela,     pvela@gatech.edu 
@date     2024/04/04            [created]

"""
#========================== perceiver.reports.channel ==========================
#!
#!NOTE:
#!  set indent to 2 spaces.
#!  do not indent function code.
#!  set tab to 4 spaces with conversion to spaces.
#!  90 columns, word margin 9 or 10. 
#
#========================== perceiver.reports.channel ==========================

from ivapy.Configuration import AlgConfig



#=================================== Channel ===================================
#

class CfgChannel(AlgConfig):
  """!
  @ingroup  Reports
  @brief    Configuration instance for a Channel.
  """

  #------------------------------ __init__ -----------------------------
  #
  def __init__(self, init_dict=None, key_list=None, new_allowed=True):
    """!
    @brief    Instantiate a channel build configuration.
    """

    if init_dict is None:
      init_dict = CfgChannel.get_default_settings()

    super(CfgChannel,self).__init__(init_dict, key_list, new_allowed)


  #------------------------ get_default_settings -----------------------
  #
  @staticmethod
  def get_default_settings():
    """!
    @brief  Get default build configuration settings for Trigger.
    """

    default_settings = dict()
    return default_settings


class Channel:
  """!
  @ingroup  Reports
  @brief    Base/abstract channel class.

  A channel implements a reporting scheme.  In the python logging API, a channel is
  similar to the combination of a handler and a formatter.  When a report is
  triggered, then the channel needs to take care of outputting to the desired
  reporting output "stream" the proper message.

  Various channel types are possible, with stdout and a text file being more typical
  examples.  Using stdout provides a similar functionality to a logger but with the
  signal to text conversion encapsulated within its processing structure.  In contrast
  a logger would be given the converted string to start with.

  The base class here implicitly uses stdout through a print statement.  Overload via
  a derived class to send elsewhere.
  """

  #============================== Channel __init__ =============================
  #
  def __init__(self, theConfig = CfgChannel()):
    """!
    @brief  Constructor for base trigger class.
    """
    self.config = theConfig

  #==================================== send ===================================
  #
  def send(self, theAnnouncement):
    print(theAnnouncement)


#==================================== toFile ===================================
#
class toFile(Channel):
  """!
  @ingroup  Reports
  @brief    Save to file channel.

  A toFile Channel saves the reports to a file.
  """

  #============================== Channel __init__ =============================
  #
  def __init__(self, theConfig = CfgChannel()):
    """!
    @brief  Constructor for base trigger class.
    """
    self.config = theConfig

    self.fid = open(self.config.filename, self.config.otype)

  #==================================== send ===================================
  #
  def send(self, theAnnouncement):
    self.fid.write(theAnnouncement)

  #================================== __del__ ==================================
  #
  def __del__(self):
    self.fid.close()

#==================================== toCSV ====================================
#
class toCSV(Channel):
  """!
  @ingroup  Reports
  @brief    Save to CSV formatted file channel.

  A toCSV Channel saves the reports to a CSV compliant file.  This channel has very
  specific usage due to the python CSV File API (See PEP 305).
  """

  #============================== Channel __init__ =============================
  #
  def __init__(self, theConfig = CfgChannel()):
    """!
    @brief  Constructor for base trigger class.
    """
    self.config = theConfig

    self.fid    = open(self.config.filename, self.config.otype, newline='')
    self.writer = csv.writer(self.fid)
    # @todo Permit external function pointer for this that has extra args.
    # @todo Or figure out how to pass extra args like eargs{:} in MATLAB.

  #================================= sendHeader ================================
  #
  def sendHeader(self, theHeader)
    self.writer.writerow(theHeader)
 
  #==================================== send ===================================
  #
  def send(self, theRow):
    self.writer.writerow(theRow)


#================================== Assignment =================================
#
class Assignment(Channel):
  """!
  @ingroup  Reports
  @brief    Assignment class for communication between BeatReporter and Editor.

  An assignment is what links a BeatReporter with and Editor.  It maintains
  information about the assignment (at minimum it's ID) and what Editor is
  attached to the BeatReporter.  The base implementation will simply pass along
  the BeatReporter's Commentary or Announcement.
  """

  #============================ Assignment __init__ ============================
  #
  def __init__(self, theConfig = CfgChannel()):
    """!
    @brief  Constructor for base trigger class.
    """
    super(self).__init__(theConfig)

    ## Assignment ID given by managing editor.
    self.id     = None
    ## Editor linked to the assignment.  Who to report news to.
    self.editor = None

  #=================================== assign ==================================
  #
  def assign(self, assignID, assignEditor):
    """!
    @brief  BeatReporter has been assigned work. Follow up on request by
            configuring a channel between (i.e., linking) Reporter and Editor.

    @param[in]  assignID        ID of assignment/beat.
    @param[in]  assignEditor    Editor managing the assignment/beat.
    """

    self.id     = assignID
    self.editor = assignEditor

  #==================================== send ===================================
  #
  def send(self, theCommentary):
    self.editor.incoming(self.id, theCommentary)

#
#========================== perceiver.reports.channel ==========================
