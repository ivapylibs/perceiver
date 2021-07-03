#============================ perceiver.simple ===========================
#
#
# @brief    A simple and general interface class for segmentation-based
#           tracking from an image stream. 
#
#
# The interface first performs detection (binary segmentation) of the
# target, then establishes a track point from the segmentation.
#
# Dependencies:
#   [function]setIfMissing   Yiye's generalized version
# 
#============================ perceiver.simple ===========================

# Import any necessary libraries/packages.



# Class description

class simple:

  #=============================== simple ==============================
  #
  # @brief  Constructor for the perceiver.simple class.
  #
  # @param[in] theDetector  The binary segmentation method.
  # @param[in] theTracker   The binary image trackpoint method.
  # @param[in] trackFilter  The track point filtering approach.
  # @param[in] theParams    Option set of paramters.
  #
  def __init__(self, theDetector, theTracker, trackFilter, theParms)

    self.detector = theDetector
    self.tracker  = theTracker
    self.filter   = trackFilter

    self.parms    = perceiver.simple.defaultParms()

    self.haveRun   = false
    self.haveObs   = false
    this.haveState = false

    self.I = MAKE_EMPTY_IMAGE

    self.tMeas = EMPTY
    # Process the run-time parameters.
    # Code missing.


  #================================ set ================================
  #
  # @brief      Set the state or parameters of the rigid body tracker.
  #
  # @param[in]  fname   Name of the field to set.
  # @param[in]  fval    Value to set.
  # 
  def set(self, fname, fval)

    switch fname
      case 'state'
        this.setState(fval);


  #================================ get ================================
  #
  # @brief      Get the state or parameters of the tracker.
  #
  # @param[in]  fname   Name of the field to set.
  # @param[out] fval    Value returned.
  #
  def fval = get(self, fname)

    switch fname
      case 'state'
        fval = self.getState(fval);
      case 'trackParms','parms'
        fval = self.parms;
      otherwise
        fval = [];
  
  
  #============================== getState %=============================
  #
  # @brief      Returns the current state structure.
  # 
  # @param  cstate  The current state structure.
  #
  def cstate = getState(self)

    #   cstate.g     = this.gFilter.getState();
    cstate.tMeas = this.tMeas;
    #   cstate.gOB   = this.gOB;
    cstate.haveObs = this.haveObs;
    cstate.haveState = this.haveState;


  #============================== setState =============================
  #
  # @brief      Sets the state of the tracker.
  #
  # @param[in]  nstate  The new state structure.
  #
  def setState(self, nstate)

  # gFilter.setState(nstate.g); NEED TO RECONSIDER HOW DONE. 
  # FOR NOW USING A PASS THROUGH BUT COMMENTING OUT.
  # self.tracker.setState(nstate);

  # EQUIVALENT TO isfield in python?
  if (isfield(nstate,'tPts'))   # Permit empty: simply won't plot.
    this.tPts = nstate.tPts;

  # Yiye had removed gOB. Not sure why. Bring back in when the
  # Lie group class package/namespace/library is up to date.
  #
  #if (isfield(nstate,'gOB') && ~isempty(nstate.gOB))
  #  this.gOB = nstate.gOB;
  #end

  this.haveObs   = nstate.haveObs;
  this.haveState = nstate.haveState;

  
  #============================= emptyState ============================
  #
  # @brief      Return state structure with no information.
  #
  # @param[out] estate  The state structure with no content.
  #
  def estate = emptyState(self)

  estate = struct('g',[],'tPts',[],'gOB',[],'haveObs',false,'haveState',false);

  
  #============================== process ==============================
  #
  # @brief  Run the tracking pipeline for one step/image measurement.
  #
  def process(self, I_rgb, I_D)

  self.predict();
  self.measure(I_rgb, I_D);
  self.correct();
  self.adapt();

  #============================ displayState ===========================
  #
  def displayState(self, dState)

    if (nargin == 1) || isempty(dState)
      dState = this.getState();
  
    this.tracker.displayState();
  
    washeld = ishold;
    hold on;
  
    if isfield(this.parms,'display')
      if isfield(this.trackParms,'dispargs')
        this.parms.display(dState, this.parms.dispargs{:});
      else
        this.parms.display(dState);
  
    if (~washeld)
      hold off;
  

  #============================ displayDebug ===========================
  #
  def displayDebug(fh, dbState)

    if (~isempty(fh))
      figure(fh);
  
    # Does nothing for now.


  #================================ info ===============================
  #
  # @brief      Return the information structure used for saving or
  #             otherwise determining the tracker setup for
  #             reproducibility.
  #
  # @param[out] tinfo   The tracking configuration information structure.
  #
  function tinfo =  info(self)

    tinfo.name    = mfilename;
    tinfo.version = '1.0.0';
    tinfo.data  = datestr(now,'yyyy/mm/dd');
    tinfo.time  = datestr(now,'HH:MM:SS');
    tinfo.parms = self.parms;

  #================================ free ===============================
  #
  # @brief      Destructor.  Just in case other stuff needs to be done.
  #
  function free(self)


# end % methods - Public 

# methods % @todo Eventually make these member functions protected and not public.


  #============================== predict ==============================
  #
  # @brief  Predict next measurement, if applicable.
  #
  function predict(self)
    
  # NOTE: this predict is designed to be any separate predictor other
  #       than that in the detector and tracker.  the component
  #       detector/tracker's predict (whole process) is executed in the
  #       measure function

  #============================== measure ==============================
  #
  # @brief  Recover track point or track frame based on detector +
  #         trackPointer output.
  #
  #
  def measure(self, I)

    # TODO: measure function is done. the tracker result is stored in the
    # this.tMeas Now finish the return state function and then test the
    # demo_simple
  
  
    # NOTE TO YUNZHI: DO NOT FOLLOW THE DESIGN PATTERN OF YIYE.
    # THE RGB-D DATA IS A UNIT AND GETS PROCESSED AS SUCH.
    # ANY NECESSARY DECOUPLED DETECTION AND POST-PROCESSING SHOULD RESIDE
    # IN THE DETECTOR USING A HIERARCHICAL STRATEGY. IF RGB-D IMAGERY IS
    # PROCESSED IN A SPECIAL WAY, THEN LET THE DETECTOR HANDLE IT.
    # IT MIGHT BE TWO SEPARATE A THREADS WITH A UNION OR INTERSECTION
    # OPERATION TO JOIN, OR IT MIGHT BE A SEQUENTIAL OPERATION. DO NOT
    # FOLLOW THE MATLAB CODE. 
    #
    # IT UNDERMINES THE SIMPLICITY OF THE PROGRAMMING AND THE FLEXIBILITY
    # OF THE INTERFACE.
  
    #! Run measurement/processing.
    
    # Image-based detection and post processing.
    self.detector.process(I);
  
    fgLayer = self.detector.getForeground()
  
    if (~isempty(self.processor)
      fgLayer = self.processor.process(fgLayer)
    
    # Tracking on binary segmentation mask.
    self.tracker.process(fgMask);
    tstate = self.tracker.getstate();
  
    self.tMeas = tstate.x;
    # MAYBE SHOULD JUST SET TO tstate IN CASE IT HAS EXTRA INFORMATION
    # THEN THIS CLASS JUST GRABS THE x FIELD. LET'S THE FIELD TAKE CARE
    # OF ITS OWN FUNCTIONALITY?
    #
    # YUNZHI: YES, GOING WITH THE ABOVE. IT MIGHT BREAK SOMETHING, BUT
    # THEN WE FIX IT.  WILL REQUIRE A Euclidean CLASS OR A
    # Lie.group.Euclidean INSTANCE (which is really just a vector).
    # SHOULD BE QUICK TO CODE UP AT ITS MOST BASIC.
  
    #if (isfield(tstate,'g'))
    #  self.tMeas = tstate.g;
    #elseif (isfield(tstate,'tpt'))
    #  self.tMeas = tstate.tpt;
    #end
  
    # self.gFilter.correct(this.tMeas); # DO WE NEED A FILTER? WHY NOT IN TRACKPOINTER?
     
    # has observation flag
    self.haveObs = ~any(isnan(this.tMeas), 'all');
    # OR IS IT: self.haveObs = ~any(isnan(this.tMeas.x), 'all');
  

  #============================== correct ==============================
  #
  # @brief  Correct the estimated state based on measured and predicted.
  #
  def correct(self)

  end

  #=============================== adapt ===============================
  #
  # @brief  Adapt parts of the process based on measurements and
  # corrections.
  #
  def adapt(self)

  end


  #=========================== displaySimple ===========================
  #
  # @brief      Basic rigid body display routine. Plots SE(2) frame.
  #
  @staticmethod
  def displaySimple(cstate, dispArgs)


  #============================ displayFull ============================
  #
  # @brief      Fill rigid body display routine. Plots SE(2) frame and
  #             marker positions.
  #
  @staticmethod
  def displayFull(cstate, dispArgs)

    wasHeld = ishold;
  
    gCurr = cstate.gOB * cstate.g;
  
    if (nargin < 2)
      dispArgs = [];
    end
  
    hold on;
  
    if isfield(dispArgs,'state')
      gCurr.plot(dispArgs.state{:});
    else
      gCurr.plot();
  
    if (isfield(dispArgs,'plotAll') && dispArgs.plotAll)
      plot(cstate.tPts(1,:), cstate.tPts(2,:), 'm+');
  
    if (isfield(dispArgs,'noTicks') && dispArgs.noTicks)
      set(gca,'YTickLabel',[],'XTickLabel',[]);
  
    drawnow;
    if (~wasHeld)
      hold off;
  

%
%============================ simple ============================
