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

import itertools

from ivapy.Configuration import AlgConfig
import perceiver.reports.channels as chans
import perceiver.reports.drafts   as Announce

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
      init_dict = BuildCfgReporter.get_default_settings()

    super(BuildCfgReporter,self).__init__(init_dict, key_list, new_allowed)


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
  def __init__(self, theTrigger, theAnnouncer, theChannel, theConfig = None):
    """!
    @brief  Constructor to reporter class.  Collects necessary pieces.

    @param[in]  theTrigger      Trigger instance.
    @param[in]  theAnnouncer    Announcer instance.
    @param[in]  theChannel      Channel instance.
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
      hasAck = self.channel.send(self.announcer.announcement)
      if hasAck:
        self.announcer.ack()

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

class CfgBeatReporter(AlgConfig):
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
      init_dict = CfgBeatReporter.get_default_settings()

    super(CfgBeatReporter,self).__init__(init_dict, key_list, new_allowed)


  #------------------------ get_default_settings -----------------------
  #
  @staticmethod
  def get_default_settings():
    """!
    @brief  Get default configuration settings for Perceiver.
    """

    default_settings = CfgReporter.get_default_settings()
    default_settings.update(dict( filterSignal = None ))
    return default_settings


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
  def __init__(self, theTrigger, theAnnouncer, theChannel = None, 
                                               theConfig = None):
    """!
    @brief  Constructor to BeatReporter class.  Collects necessary pieces.

    @param[in]  theTrigger      Trigger instance.
    @param[in]  theAnnouncer    Announcer instance.
    @param[in]  theChannel      Channel instance (optional).
    @param[in]  theConfig       Configuration specifications (optional).
    """

    # Something weird was happening that when Channel = chans.Assignment() was
    # set to be the default argument, it always pointed to the same instance and
    # not to newly created instances.  Apparently, python has this behavior by
    # design. See below:
    #
    # https://medium.com/@nebiyuelias1/be-careful-when-using-default-arguments-in-python-fd92df94efee
    # https://www.reddit.com/r/learnpython/comments/118ucmz/why_do_python_functions_reuse_pointer_to_mutable/
    # https://www.reddit.com/r/learnpython/comments/118ucmz/why_do_python_functions_reuse_pointer_to_mutable/
    #
    # This behavior was ruining the assignment instances for each BeatReporter.
    # The fix is super easy and aligns with how coded in other locations (somehow
    # decided by accident or by having code work that way and subconciously resolving).
    # Part is also due to following pattern of coding set by others.
    # It's kind of annoying, but easy to resolve and to avoid once known.
    # Also introduced me to concept of a sentinal value, which is a design paradigm
    # and description to remember:
    #
    # https://en.wikipedia.org/wiki/Sentinel_value
    #
    # Leaving here in case it helps others know why the above default arguments
    # are pretty standard. Especially others who learn python by doing and not in
    # a formal class.

    if theChannel is None:
      theChannel = chans.Assignment()

    if theConfig is None:
      theConfig = CfgBeatReporter();

    #DEBUG
    #print("BR init:")
    #print(type(theChannel))
    #print(type(theConfig))
    #print(theChannel)
    #print(chans.Assignment())

    super(BeatReporter,self).__init__(theTrigger, theAnnouncer, theChannel, theConfig)

    ## Flag indicating whether the BeatReporter has an assignment from an Editor.
    self.hasAssignment  = False
    ## Flag indicating whether the BeatReporter is on assignment (i.e., reporting).
    self.isOnAssignment = False

    #DEBUG
    #print(self.channel)

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

    self.channel.assign(assignID, theEditor)
    self.isOnAssignment = True
    self.hasAssignment  = True

  #================================= pauseBeat =================================
  #
  def pauseBeat(self):
    """!
    @brief  Pause assignment.  
    
    When an assignment is paused, the BeatReporter will not report to Editor.
    In fact, the default for the class is to not even process triggers.
    Subclasses can overload this operational scheme and continue processing triggers
    but without reporting the outcomes to the Editor. 
    """
    self.isOnAssignment= False

  #================================= resumeBeat ================================
  #
  def resumeBeat(self):
    """!
    @brief  Resume assignment.  Will report to Editor when triggered.

    Resume a paused beat assignment.
    """

    if self.hasAssignment:
      self.isOnAssignment = True

  #================================ unassignBeat ===============================
  #
  def pauseBeat(self):
    """!
    @brief  Pause assignment.  
    
    When an assignment is paused, the BeatReporter will not report to Editor.
    In fact, the default for the class is to not even process triggers.
    Subclasses can overload this operational scheme and continue processing triggers
    but without reporting the outcomes to the Editor. 
    """
    self.isOnAssignment = False

  #================================== process ==================================
  #
  def process(self, theSignal):
    """!
    @brief  Process incoming signal and report as specified.

    @param[in]  theSignal   Signal to process for reporting.

    @return     Passes back trigger outcome, in case helpful.
    """

    if self.isOnAssignment and self.trigger.test(theSignal):

      if (self.config.filterSignal is None):
        self.announcer.prepare(theSignal)
      else:
        self.announcer.prepare(self.config.filterSignal(theSignal))

      hasAck = self.channel.send(self.announcer.message())

      if hasAck:
        self.announcer.ack()

      return True
    else:
      return False


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


  #========================= buildGroupWithAnnouncement ========================
  #
  @staticmethod
  def buildGroupWithAnnouncement(triggers = None, announceFuns = None, 
                 announceCfg = None, 
                 beatrepCfg = None):
    """!
    @brief  Build out a group of BeatReporter instances.

    @param[in]  triggers        List of triggers. Required. Determines no. of BeatReporters
    @param[in]  announceFuns    Not provided or List of announcement function pointers.
    @param[in]  announceCfg     Not provided, singleton, or list of announcement configs. 
    @param[in]  beatrepCfg      Not provided, singleton, or list of reporter configs. 

    Uses the passed arguments to build out a group of reporters.  The list of Triggers
    is crucial since there should be one per BeatReporter.  Then, there should be
    enough information in announceFuns or announceCfgs to instantiate one Announcement
    per Trigger.  Either enough announceFuns and an announceCfg exists to instantiate
    multiple Announcements, one per announceFun (in principle equal in number to the
    quantity of Triggers).  Or no announceFuns and enough announceCfg instances to
    create multiple Announcements.

    The BeatReporter configuration can be given or not.  It will use a default
    configuration if not provided.
    """

    # If no triggers, then there is not enough information to set things up.
    # The number of triggers sets the downstream processing.
    if triggers is None:
      return None

    if (announceCfg is None):
      announceCfg = Announce.CfgAnnouncement()

    if (beatrepCfg is None):
      beatrepCfg = CfgBeatReporter()
  
    if (len(beatrepCfg) == 0):
      theBRCfgs = list()
      for ii in range(len(triggers)):
        theBRCfgs.append( beatrepCfg.clone() )
      beatrepCfg = theBRCfgs
  
    if announceFuns is None:  # No function points, then must have multiple configs.
      if len(announceCfg) == len(triggers):   # One for each trigger.
        brGroup = []
        for i in range(len(triggers)):
          announce = Announce.Announcement(announceCfg[i])
          brGroup.append( BeatReporter(triggers[i], announce, theConfig = beatrepCfg[i]) )
      else:
        return None

    elif len(announceFuns) == len(triggers):  

      brGroup = []
      for i in range(len(triggers)):

        currCfg = announceCfg.clone()
        currCfg.signal2text = announceFuns[i]
        announce = Announce.Announcement(currCfg)

        brGroup.append( BeatReporter(triggers[i], announce, theConfig = beatrepCfg[i]))

    else:
      return None

    return brGroup

  #======================== buildGroupWithCommentary ========================
  #
  @staticmethod
  def buildGroupWithCommentary(triggers = None, announceFuns = None, 
                 commentFuns = None, commentCfg = None,
                 beatrepCfg = None):
    """!
    @brief  Build out a group of BeatReporter instances.

    @param[in]  triggers        List of triggers. Required. Determines no. of BeatReporters
    @param[in]  announceFuns    Not provided or List of commentary function pointers.
    @param[in]  commentFuns     Not provided or List of commentary function pointers.
    @param[in]  commentCfg      Not provided, singleton, or list of announcement configs. 
    @param[in]  beatrepCfg      Not provided, singleton, or list of reporter configs. 

    Uses the passed arguments to build out a group of reporters.  The list of Triggers
    is crucial since there should be one per BeatReporter.  Then, there should be
    enough information in announceFuns+commentFuns or commentCfgs to instantiate one
    Announcement per Trigger.  Either enough announceFuns+commentFuns and an
    commentCfg exists to instantiate multiple Commentary, one per commentFun (in
    principle equal in number to the quantity of Triggers).  Or no
    announceFuns+commentFuns and enough commentCfg instances to create multiple
    Commentaries.

    The BeatReporter configuration can be given or not.  It will use a default
    configuration if not provided.
    """

    # If no triggers, then there is not enough information to set things up.
    # The number of triggers sets the downstream processing.
    if triggers is None:
      return None

    if commentCfg is None:
      commentCfg = Announce.CfgCommentary()

    if beatrepCfg is None:
      beatrepCfg = CfgBeatReporter()
  
    if (len(beatrepCfg) == 0):
      theBRCfgs = list()
      for ii in range(len(triggers)):
        theBRCfgs.append( beatrepCfg.clone() )
      beatrepCfg = theBRCfgs
  
    if (announceFuns is None):
      announceFuns = list(itertools.repeat(announceFuns, len(triggers)))
    elif announceFuns.__class__ == list and (len(announceFuns) == 1):
      announceFuns = list(itertools.repeat(announceFuns[1], len(triggers)))
    else:
      announceFuns = list(itertools.repeat(announceFuns, len(triggers)))

    if commentFuns is None:
      if len(commentCfg) == len(triggers):   # One for each trigger.
        brGroup = []
        for i in range(len(triggers)):
          announce = Announce.Commentary(commentCfg[i])
          brGroup.append( BeatReporter(triggers[i], announce, theConfig = beatrepCfg[i]) )
      else:
        return None

    elif len(commentFuns) == len(triggers):  

      brGroup = []
      for i in range(len(triggers)):

        currCfg = commentCfg.clone()
        currCfg.signal2text = announceFuns[i]
        currCfg.signalsaver = commentFuns[i]
        announce = Announce.Commentary(currCfg)

        brGroup.append( BeatReporter(triggers[i], announce, theConfig = beatrepCfg[i]))

    else:
      return None

    return brGroup

  #====================== buildGroupWithRunningCommentary ======================
  #
  @staticmethod
  def buildGroupWithRunningCommentary(triggers = None, keepQuiet = False, filters = None,
                 announceFun = None, commentFun = None, commentCfg = None,
                 beatrepCfg = None):
    """!
    @brief  Build out a group of BeatReporter instances with Running Commentary.

    @param[in]  triggers        List of triggers. Required. Determines no. of BeatReporters
    @param[in]  keepQuiet       Singleton or list indicating assignment reporting property.
    @param[in]  commentCfg      Not provided, singleton, or list of announcement configs. 
    @param[in]  beatrepCfg      Not provided, singleton, or list of reporter configs. 


    The way that a single RunningCommentary works is that all signal feeds get sent to
    the instance and accumulated.  During accumulation, the Editor should not receive
    any notification.  However, one assignment or multiple specific assignments should
    indicate that accumulated information is ready to go.   All others do not send the
    information to the Editor for action.  There are many different ways to achieve
    this kind of processing.  The current design was the simplest based on what was
    built out.

    Because there is only a single Commentary instance that absorbs all information,
    there is no need to provide multiple comment and announcement functions, just one
    for each if it is custom.  Otherwise, the default is for the commentfun to be a
    passthrough and the announceFun to be None.  If the announceFun is not none, it
    should permit as input the commenFun output (which in the default case is an
    iterable).

    Uses the passed arguments to build out a group of reporters.  The list of Triggers
    is crucial since there should be one per BeatReporter.  If the assignment or beat
    that triggers an output matters, then keepQuiet boolean list should indicate which
    one it is. Otherwise, all beat assignments will not keep quiet.

    Then, there should be
    enough information in announceFuns+commentFuns or commentCfgs to instantiate one
    Announcement per Trigger.  Either enough announceFuns+commentFuns and an
    commentCfg exists, one per commentFun (in principle equal in number to the
    quantity of Triggers).  Or no announceFuns+commentFuns and enough commentCfg
    instances.  All are given the same RunningCommentary.  The Editor instance
    controls the decision to output.

    The BeatReporter configuration can be given or not.  It will use a default
    configuration if not provided.
    """

    # If no triggers, then there is not enough information to set things up.
    # The number of triggers sets the downstream processing.
    if triggers is None:
      return None

    if len(keepQuiet) == 0:
      keepQuiet = list(itertools.repeat(keepQuiet, len(triggers)))
    elif len(keepQuiet) != len(triggers):
      return None
      # @todo How should invalid setup be dealt with?

    if filters is None:
      filters = list(itertools.repeat(filters, len(triggers)))
    elif len(filters) != len(triggers):
      return None
      # @todo How should invalid setup be dealt with?

    if (commentCfg is None):
      commentCfg = Announce.CfgRunningCommentary()

    if (commentFun is None):
      commentFun = Announce.Announcement.passthrough

    commentCfg.signal2text = announceFun
    commentCfg.signalsaver = commentFun

    if (beatrepCfg is None):
      beatrepCfg = CfgBeatReporter()
  
    if (beatrepCfg.__class__  != list):
      theBRCfgs = list()
      for ii in range(len(triggers)):
        theBRCfgs.append( beatrepCfg.clone() )
      beatrepCfg = theBRCfgs
  
    announce = Announce.RunningCommentary(commentCfg)
    brGroup  = []

    for ii in range(len(triggers)):
      beatrepCfg[ii].filterSignal = filters[ii]
      bReportr = BeatReporter(triggers[ii], announce, theConfig = beatrepCfg[ii]) 
      bReportr.channel.keepQuiet = keepQuiet[ii]

      brGroup.append( bReportr )


    return brGroup


# @todo Create a buildGroupIteratively that has everything packed into iterable
#       elements.  Just in case want to create more custom instances in a generic
#       manner.  Imagine having two running commentaries that trigger output.
#       Like for CSV, where one line has certain information, and a second line
#       has related information. Can be triggered at same time, but output 
#       different information to same stream.
#       Skipping for now since not needed, but may eventually be necessary.
#       How do we internalize within ROS as needed???

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
  (or report out) and in what order.   We call the Editor level receipt of activity
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

    @param[in]  theChannel     Channel instance.
    @param[in]  theConfig       Configuration specifications.
    """

    if (theConfig is None):
      theConfig = CfgEditor()

    ## List of BeatReporters to manage (replaces role of Triggers).
    self.reporters = list()             
    ## Final output channel for all reports.
    self.channel   = theChannel     
    ## Configuration of Editor
    self.config    = theConfig      
    ## List of Revision filters for BeatReporter Commentary (optional).
    self.revisions = list()             

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

    nEl = len(self.reporters)
    #DEBUG
    #print('addBeat: ' + str(nEl))

    #if (self.config.autoAssign):    # WHAT IS GOING ON HERE??? WHERE IS AUTOASSIGN?
    if assignID is None:
      assignID = nEl

    self.reporters.append(beatReporter)
    self.revisions.append(beatRevisor)

    beatReporter.assignBeat(self, assignID)

    # @todo Or is this done by the channel?
    # @todo Figure out whether Editor configures things or channel construction
    #       does it. Or some mix?  Maybe channel is its own type but gets
    #       managed by the Editor.

  #================================ assignGroup ================================
  #
  def assignGroup(self, theGroup, theRevisor = None, assignIDs = None):
    """!
    @brief  Assign a group of BeatReporters to the Editor.
    """

    if (theRevisor is None) or (len(theRevisor) == 0) :
      theRevisor = list(itertools.repeat(theRevisor, len(theGroup)))

    if (assignIDs is None) or (len(assignIDs) !=  len(theGroup)):    
      assignIDs = list(itertools.repeat(None, len(theGroup)))

    for bi in range(len(theGroup)):
      self.addBeat(theGroup[bi], theRevisor[bi], assignIDs[bi])

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

    if (assignID >= 0) and (assignID < len(self.reporters)):
      # @warning    Not good.  First find index by ID. Then remove
      #             from reporter list and revision list.
      #             Then unassign and whatever else.
      #
      # @note       Actually, looks kosher as reporters get new assignment IDs
      #             in the for loop just below.  what is good way to manage?
      #             What is Editor uses ordering or assignID to decide what
      #             to do?  This can cause problems. To resolve later.
      #
      theReporter = self.reporters.pop(assignID)
      self.revision.pop(assignID)

      theReporter.unAssign();
      # TODO:   BeatReporter needs isOnAssignment or onAssignment

      for ii in range(assignID,len(self.reporters)):
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

    #DEBUG
    #print('Editor: incoming. ' + str(assignID))
    #print(theReport)
    #print(type(theReport))
    if (assignID >= 0) and (assignID < len(self.reporters)):
      
      if (self.revisions[assignID] is None):
        if theReport is not None:
          self.channel.send(theReport)
          # self.reporter(assignID).getCommentary)
      else:
        self.channel.send(self.revisions(assignID).review(theReport))

    # TODO: Just made up how operates above.  Review function invocations and
    #       correct as needed.



#
#============================= perceiver.reporting =============================
