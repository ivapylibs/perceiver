#============================= perceiver.reporting =============================
"""!

Python package/module with top-level API for reporting outcomes of a perceived scene.
See Perceiver/Reports doxygen page for more details.

@author   Patricio A. Vela,     pvela@gatech.edu 
@date     2024/02/24            [created]

"""
#============================= perceiver.reporting =============================
#!
#!NOTE:
#!  set indent to 2 spaces.
#!  do not indent function code.
#!  set tab to 4 spaces with conversion to spaces.
#!  90 columns 
#
#============================= perceiver.reporting =============================

from ivapy.Configuration import AlgConfig
import perceiver.reports.channels as chans

#=============================== BuildCfgReporter ==============================
#

class BuildCfgReporter(AlgConfig):
  """!
  @ingroup  Reports
  @brief    Configuration instance for a Reporter.

  Instantiating a reporter usually requires a trigger and an announcer.  The
  trigger uses history of the state to report, or possible other externally
  derived states, to estalish when to "announce" a given piece of information.
  The announcer then pipes the message or announcement to the proper channel.

  All of the core implementations are overloadable through derived classes.
  Some generic versions are available.

  @warning  NOT IMPLEMENTED.  JUST STUB CODE AS OF NOW.
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

class CfgReporter(AlgConfig):
  """!
  @ingroup  Reports
  @brief    Configuration instance for a Reporter.

  @warning  NOT IMPLEMENTED.  JUST STUB CODE AS OF NOW.
  """

  #------------------------------ __init__ -----------------------------
  #
  def __init__(self, init_dict=None, key_list=None, new_allowed=True):
    '''!
    @brief    Instantiate a Reporter configuration element.
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


class Reporter:
  """!
  @ingroup  Reports
  @brief    Base/abstract reporter class.

  A Reporter consists of a Trigger, an Announcer, and a Channel for a given state
  stream.  The Trigger uses state/signal history--or possible other externally derived 
  states--to establish when to "announce" a given piece of information.
  The Announcer then constructs the necessary announcement to then be piped through
  the proper Channel.

  It is like a more flexible logging system with some of its structural elements.
  For example, the python logging API has loggers, handlers, filters, and formatters.
  Their analogs are reporters, channels, and triggers, with announcers being somewhat
  distinct. Based on intended use, a reporter is not the same as a logger.  First, the
  information given is not necessarily a string. Second, specific meta-data that
  normally gets output by the logger may not apply here and other meta-data may be of
  interest.  The caller will usually have created the reporter to use as needed,
  as opposed to being generally used by all code.  Also, a logger is called when
  logging needed.  Here, a reporter gets called all the time with updated state
  information.  It decides (based on the trigger) when to report and how (based on the
  announcer).

  A reporter manages the higher level flow that goes from state information to output.
  This way programming can go from debug type outputs to highly structured output that
  supports analysis.  It can even be that the output is to a stream, thereby serving as
  input to some other process. Such a case could hold for ROS topic/message output types.

  All of the core implementations are overloadable through derived classes.
  Some generic versions are available.
  """

  #================================== __init__ =================================
  #
  def __init__(self, theTrigger, theAnnouncer, theChannel, theConfig = CfgReporter()):
    """!
    @brief  Constructor to reporter class.  Collects necessary pieces.

    @param[in]  theTrigger      Trigger instance.
    @param[in]  theAnnouncer    Announcer instance.
    @param[in]  theChanncel     Channel instance.
    @param[in]  theConfig       Configuration specifications.
    """

    if (theConfig is None):
      theConfig = CfgReporter()

    self.trigger   = theTrigger
    self.announcer = theAnnouncer
    self.channel   = theChannel
    self.config    = theConfig


  #================================== process ==================================
  #
  def process(self, theSignal):
    """!
    @brief  Process incoming signal and report as specified.

    @param[in]  theSignal   Signal to process for reporting.

    @return     Passes back trigger outcome, in case helpful.
    """

    if (self.trigger.test(theSignal)):
      self.announcer.prepare(theSignal)
      self.channel.send(self.announcer.announcement)
      return True
    else:
      return False


# NOT SURE WHAT THIS WAS INTENDED TO BE!!
# MAYBE A SPECIALIZED CONSTRUCTION THE REQUIRED LESS PIECES DUE TO
# THEIR BEING UNIQUE AND AUTO-BUILT IN THE CONSTRUCTOR??
#
# SEEMS LIKE THIS IS ABOUT CREATING A REPORTER FOR A STATUS TYPE (FLAG OR ENUM).
#class RepStatus(Reporter):
#  __init__


#================================= BeatReporter ================================
#

class BeatReporter(Reporter):
  """!
  @ingroup  Reports
  @brief    Specialized reporter class that works with an editor.

  A BeatReporter consists of the same elements as a Reporter but its individual
  components process the information differently and reports out to an editor.  
  A BeatReporter is responsible for creating specific reporting output that is shared
  with the editor.  The Editor then collects the output and determines when to publish
  (or report out) and in what order.  Consequently, the channel output of a
  BeatReporter is not the final output channel but goes to the Editor's "news desk."
  The Editor's channel actually does the reporting through a output generating
  channel.

  @note Right now a lot of the core is done by the Reporter and there really is no
        need for a special derived class.  Should we stick with it, should we 
        add a build static method to Reporter for a BeatReporter configuration,
        or something else? Just in case something changes, going with a separate
        class as it might interact with the Editor in a unique way.  Otherwise, this
        separation may remain as an example of "the code is the documentation."
  """

  #================================== __init__ =================================
  #
  def __init__(self, theTrigger, theAnnouncer, theChannel = chans.Assignment(), \
                                               theConfig = CfgReporter()):
    """!
    @brief  Constructor to BeatReporter class.  Collects necessary pieces.

    @param[in]  theTrigger      Trigger instance.
    @param[in]  theAnnouncer    Announcer instance.
    @param[in]  theChanncel     Channel instance (optional).
    @param[in]  theConfig       Configuration specifications (optional).
    """

    super(self).__init__(theTrigger, theAnnouncer, theChannel, theConfig)

    ## Flag indicating whether the BeatReporter is on assignment.
    self.isOnAssignment = False

  #================================= assignBeat ================================
  #
  def assignBeat(self, theEditor, assignID):
    """!
    @brief  Put on assignment by linking up with an Editor.

    This member function is usually invoked by the Editor and carries out the
    work of setting up the assignment.  Default is a pass through to the Channel,
    which should be of Assignment class.

    @param[in]  theEditor   Editor managing the reporter.
    @param[in]  assignID    Assignment ID given (usually outer scope is Editor).
    """

    self.channel.assign(theEditor, assignID)
    self.isOnAssignment= True

  #=============================== assignToEditor ==============================
  #
  def assignToEditor(self, theEditor, beatRevisor = None, assignID = None):
    """!
    @brief  Have beat reporter self-assign to Editor.  Though exists, not a
            typical way to invoke. Better for request to come from Editor based
            on outer-outer scope invocation.

    @param[in]  theEditor       Editor who BeatReporter should report to.
    @param[in]  beatRevisor     To revise reporters commentary output, if needed.
    @param[in]  assignID        Assignment ID. If not given, automatically done. 
    """

    theEditor.addBeat(self, beatRevisor, assignID)



#==================================== Editor ===================================
#

class Editor:
  """!
  @ingroup  Reports
  @brief    Editor class manages multiple reporters and curates information going to
            the output channel based on reporter commentary.


  An Editor manages multiple reporters that are given "assignments" in that they
  receive specific signals, have their own triggers, and respond to the associated
  signals in their own ways.
  An Editor collects the reporter outputs and determines when to publish
  (or report out) and in what order.   We can the Editor level receipt of activity
  as the the Editor's "news desk." The Editor's collects the information and its
  channel does the reporting through a output generating channel.

  Typically the Editor will have a set of BeatReporters that are responsible for
  creating specific reporting output.  All of their streams are integrated into a
  single output stream (or channel).
  """

  #================================== __init__ =================================
  #
  def __init__(self, theChannel, theConfig = CfgReporter()):
    """!
    @brief  Constructor to Editor class.  Collects necessary pieces.

    The constructor is not as rich as the Reporter because it maintains a list
    of Reporters that contain the necessary action responses to events.  The
    Editor simply manages the responses from BeatReporters and submits the
    output to its own channel, which is given here in the constructor.

    The base design will operate a lot like a standard logging system whereby
    all Reporters will simply output through the same channel.  In principle,
    managing this way is not needed since multiple independent reporters can
    simply share a channel and operate that way.  For more specialized
    operation, use sub-classes and override the default operation.

    @param[in]  theChanncel     Channel instance.
    @param[in]  theConfig       Configuration specifications.
    """

    if (theConfig is None):
      theConfig = CfgReporter()

    ## Final output channel for all reports.
    self.channel   = theChannel     
    ## Configuration of Editor
    self.config    = theConfig      
    ## List of BeatReporters to manage.
    self.reporters = []             
    ## List of Revision filters for BeatReporter Commentary (optional).
    self.revisions = []             

  #================================== addBeat ==================================
  #
  def addBeat(self, beatReporter, beatRevisor = None, assignID = None):
    """!
    @brief  Add a new BeatReporter to manage and potentially provide a news desk
            assignment ID (default is true for this last part).

    @param[in]  beatReporter    Tell editor to manage new beat reporter.
    @param[in]  beatRevisor     To revise reporters commentary output, if needed.
    @param[in]  assignID        Assignment ID. If not given, automatically done. 
    """

    nEl = self.reporters.len()

    if (autoAssign)
      assignID = nEl + 1

    self.reporters.add(beatReporter)
    self.revisions.add(beatRevisor)

    beatReporter.onAssignment(assignID, self)

    # @todo Or is this done by the channel?
    # @todo Figure out whether Editor configures things or channel construction
    #       does it. Or some mix?  Maybe channel is its own type but gets
    #       managed by the Editor.

  #================================== remBeat ==================================
  #
  def remBeat(self, assignID):
    """!
    @brief  Remove BeatReporter based on provided assignment ID. 

    If the assignment ID is non-sensical (out of bounds), then the request
    is ignored.  Currently no indication is provided for this outcome.

    The default version of the Editor maintains a list of BeatReporters whose
    assignment IDs match their placement in the list.  Removing a beat
    reshuffles the list and triggers updated assignment IDs.  If outer
    processing requires static IDs, then this class needs to be overloaded.
    Or, it might be better for outer scope to use the Reporter handle.
    That might be problematic if the outer scope is not privy to assignment
    status.  Should query BeatReporter to know if it is on assignment. 

    @param[in]  assignID    Assignment ID of reporter.
    """

    if (assignID >= 0) and (assignID < self.reporters.len()):
      theReporter = self.reporters.pop(assignID)
      self.revision.del(assignID)

      theReporter.unAssign();
      # TODO:   BeatReporter needs isOnAssignment or onAssignment

      for ii in range(assignID:self.reporters.len()):
        self.reporters(ii).newAssignment(ii)


  #================================== incoming =================================
  #
  def incoming(self, assignID, theReport):
    """!
    @brief  There is an incoming output from a BeatReporter.  Process based on
            assignment ID.

    The default Editor simply has a bunch of BeatReporters and gives them IDs
    according to order attached to the Editor.  This gives placement in the
    list.  
    
    If more specialized processing with interactions between BeatReporters is
    needed, then this Editor class should be overloaded so that assigment
    conditional output and assigment coordinated output may be implemented.
    Or so that assignment ID involves a lookup to be unbound from ordering.

    @param[in]  assignID    Assignment ID
    @param[in]  theReport   Report generated by the BeatReporter.
    """

    if (assignID >= 0) and (assignID < self.reporters.len()):
      
      if (self.revisions(assignID)):
        self.channel.send(self.revisions(assignID).review(theReport))
      else:
        self.channel.report(theReport)
            # self.reporter(assignID).getCommentary)

    # TODO: Just made up how operates above.  Review function invocations and
    #       correct as needed.



#
#============================= perceiver.reporting =============================
