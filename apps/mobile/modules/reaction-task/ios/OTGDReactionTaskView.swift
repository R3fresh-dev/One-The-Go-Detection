import UIKit
import QuartzCore
import CallKit
import ExpoModulesCore

final class ReactionViewRegistry {
  static let views = NSHashTable<OTGDReactionTaskView>.weakObjects()
  static func stopAll(_ reason: String) {
    if Thread.isMainThread { views.allObjects.forEach { $0.stop(reason) } }
    else { DispatchQueue.main.async { views.allObjects.forEach { $0.stop(reason) } } }
  }
}
private final class ReactionDisplayTarget: NSObject {
  weak var view: OTGDReactionTaskView?
  @objc func tick(_ link: CADisplayLink) { view?.frame(link) }
}
private final class ReactionInputButton: UIButton {
  weak var taskView: OTGDReactionTaskView?
  override func touchesBegan(_ touches: Set<UITouch>, with event: UIEvent?) { taskView?.receive(touches, event: event); super.touchesBegan(touches, with: event) }
  override func touchesEnded(_ touches: Set<UITouch>, with event: UIEvent?) { taskView?.release(touches); super.touchesEnded(touches, with: event) }
  override func touchesCancelled(_ touches: Set<UITouch>, with event: UIEvent?) { taskView?.stop("INPUT_CANCELED"); taskView?.release(touches); super.touchesCancelled(touches, with: event) }
}

final class OTGDReactionTaskView: ExpoView, CXCallObserverDelegate {
  let onProgress = EventDispatcher()
  let onComplete = EventDispatcher()
  var requestedRunId = ""
  var requestedSeed = 0.0
  var requestedRunning = false
  var requestedConfigurationId = ""
  var requestedConfigurationHash = ""
  var requestedEpoch = ""
  private var active = false
  private var runId = ""
  private var epoch = ""
  private var seed: UInt32 = 0
  private var startMs = 0.0
  private var startWall = Date()
  private var frozenBounds = CGRect.zero
  private var nextTrial = 0
  private var visibleStimulus: String? = nil
  private var trials: [ReactionTrial] = []
  private var inputs: [ReactionInput] = []
  private var seenRuns: Set<String> = []
  private var flags: [String] = []
  private var terminalCutoff: Double? = nil
  private var terminalLatch = ReactionTerminalLatch()
  private var terminalResult: [String: Any]?
  private var lastFrame: Double? = nil
  private var lastCallbackMs = 0.0
  private var maxGap = 0.0
  private var maxFrameDispatch = 0.0
  private var maxInputDispatch = 0.0
  private var overflowCount = 0
  private var pointerIds: [ObjectIdentifier: Int] = [:]
  private var nextPointerId = 0
  private var displayLink: CADisplayLink?
  private let displayTarget = ReactionDisplayTarget()
  private var watchdog: DispatchSourceTimer?
  private var observers: [NSObjectProtocol] = []
  private let callObserver = CXCallObserver()
  private let left = ReactionInputButton(frame: .zero)
  private let right = ReactionInputButton(frame: .zero)
  private let end = ReactionInputButton(frame: .zero)

  required init(appContext: AppContext? = nil) {
    super.init(appContext: appContext)
    clipsToBounds = true; isMultipleTouchEnabled = true; backgroundColor = color(0x101820)
    configure(left, title: "Left", size: 20, fill: 0x213547)
    configure(right, title: "Right", size: 20, fill: 0x213547)
    configure(end, title: "End task", size: 16, fill: 0x334155)
    end.addTarget(self, action: #selector(endAction), for: .primaryActionTriggered)
    displayTarget.view = self; ReactionViewRegistry.views.add(self)
    observers.append(NotificationCenter.default.addObserver(forName: UIApplication.willResignActiveNotification, object: nil, queue: .main) { [weak self] _ in self?.stop("FOCUS_LOST") })
    observers.append(NotificationCenter.default.addObserver(forName: UIApplication.didEnterBackgroundNotification, object: nil, queue: .main) { [weak self] _ in self?.stop("BACKGROUND") })
    observers.append(NotificationCenter.default.addObserver(forName: UIAccessibility.voiceOverStatusDidChangeNotification, object: nil, queue: .main) { [weak self] _ in self?.stop("INPUT_MODE_UNSUPPORTED") })
  }
  deinit {
    displayLink?.invalidate(); watchdog?.cancel(); callObserver.setDelegate(nil, queue: nil)
    observers.forEach { NotificationCenter.default.removeObserver($0) }
  }
  private func configure(_ button: ReactionInputButton, title: String, size: CGFloat, fill: UInt32) {
    button.taskView = self; button.setTitle(title, for: .normal); button.accessibilityLabel = title
    button.titleLabel?.font = UIFont.systemFont(ofSize: size, weight: .regular)
    button.titleLabel?.adjustsFontForContentSizeCategory = false
    button.titleLabel?.numberOfLines = 2; button.titleLabel?.textAlignment = .center
    button.setTitleColor(.white, for: .normal); button.setTitleColor(.white, for: .highlighted)
    button.backgroundColor = color(fill); button.layer.cornerRadius = 12
    button.layer.borderColor = color(0x71899E).cgColor; button.layer.borderWidth = 2
    button.isMultipleTouchEnabled = true; addSubview(button)
  }
  private func rect(_ x: CGFloat, _ y: CGFloat, _ width: CGFloat, _ height: CGFloat) -> CGRect {
    CGRect(x: bounds.width*x/1000, y: bounds.height*y/1000, width: bounds.width*width/1000, height: bounds.height*height/1000)
  }
  private var leftRect: CGRect { rect(20,650,460,250) }
  private var rightRect: CGRect { rect(520,650,460,250) }
  private var endRect: CGRect { rect(750,20,230,120) }
  override func layoutSubviews() {
    super.layoutSubviews()
    if active && bounds.size != frozenBounds.size { stop("LAYOUT_CHANGED") }
    left.frame = leftRect; right.frame = rightRect; end.frame = endRect
    commitProps()
  }
  override func willMove(toWindow newWindow: UIWindow?) { if newWindow == nil { stop("VIEW_DETACHED") }; super.willMove(toWindow: newWindow) }
  override func didMoveToWindow() { super.didMoveToWindow(); commitProps() }
  @objc private func endAction() { stop("USER_CANCELED") }

  func commitProps() {
    if active && (!requestedRunning || requestedRunId != runId || requestedEpoch != epoch || requestedSeed != Double(seed) || requestedConfigurationId != ReactionConfig.id || requestedConfigurationHash != ReactionConfig.sha256) {
      stop(requestedEpoch != epoch ? "WORKSPACE_CHANGED" : "USER_CANCELED")
    }
    guard requestedRunning, !active, !seenRuns.contains(requestedRunId), window != nil, bounds.width > 0, bounds.height > 0, UIApplication.shared.applicationState == .active else { return }
    // Props are application-controlled; malformed values never become a fabricated seed or identity.
    guard UUID(uuidString: requestedRunId) != nil, !requestedEpoch.isEmpty, requestedEpoch.count <= 128,
          requestedSeed.isFinite, requestedSeed >= 0, requestedSeed <= Double(UInt32.max), requestedSeed.rounded(.towardZero) == requestedSeed,
          seenRuns.count < 128 else { return }
    initializeRun()
    guard requestedConfigurationId == ReactionConfig.id, requestedConfigurationHash == ReactionConfig.sha256 else { stop("CONFIGURATION_MISMATCH"); return }
    guard bounds.width >= 240, bounds.height >= 400, bounds.width <= bounds.height else { stop("LAYOUT_UNSUPPORTED"); return }
    guard !UIAccessibility.isVoiceOverRunning else { stop("INPUT_MODE_UNSUPPORTED"); return }
    callObserver.setDelegate(self, queue: .main)
    guard !callObserver.calls.contains(where: { !$0.hasEnded }) else { stop("CALL_INTERRUPTION"); return }
    let link = CADisplayLink(target: displayTarget, selector: #selector(ReactionDisplayTarget.tick(_:)))
    displayLink = link; link.add(to: .main, forMode: .common)
    let timer = DispatchSource.makeTimerSource(queue: .main)
    timer.schedule(deadline: .now() + .milliseconds(20), repeating: .milliseconds(20))
    timer.setEventHandler { [weak self] in self?.watchdogTick() }; watchdog = timer; timer.resume(); setNeedsDisplay()
  }
  private func initializeRun() {
    runId = requestedRunId; epoch = requestedEpoch; seed = UInt32(requestedSeed); seenRuns.insert(runId)
    startMs = clockMs(); startWall = Date(); frozenBounds = bounds
    trials = ReactionCore.schedule(seed: seed); inputs.removeAll(keepingCapacity: true); flags = ["UNCALIBRATED_TIMING"]
    nextTrial = 0; visibleStimulus = nil; terminalCutoff = nil; terminalResult = nil; lastFrame = nil; lastCallbackMs = startMs
    maxGap = 0; maxFrameDispatch = 0; maxInputDispatch = 0; overflowCount = 0; pointerIds.removeAll(); nextPointerId = 0; active = true; terminalLatch = ReactionTerminalLatch()
  }
  func callObserver(_ callObserver: CXCallObserver, callChanged call: CXCall) { if !call.hasEnded { stop("CALL_INTERRUPTION") } }
  private func watchdogTick() {
    guard active else { return }
    let now = clockMs()
    if let cutoff = terminalCutoff, now-startMs >= cutoff { finishAtCutoff(); return }
    if now-lastCallbackMs > ReactionConfig.budgetMs { stop("FRAME_CALLBACK_DELAY_EXCEEDED"); return }
    if nextTrial < trials.count && now-startMs > Double(trials[nextTrial].plannedOnsetMs)+ReactionConfig.budgetMs { stop("SCHEDULED_ONSET_LATE") }
  }
  fileprivate func frame(_ link: CADisplayLink) {
    guard active else { return }
    let now = clockMs(); let relative = now-startMs
    if let cutoff = terminalCutoff, relative >= cutoff { finishAtCutoff(); return }
    guard window != nil, !isHidden, alpha > 0, UIApplication.shared.applicationState == .active else { stop("FOCUS_LOST"); return }
    let frame = link.timestamp*1000; let estimate = link.targetTimestamp*1000-startMs
    let gap = lastFrame.map { frame-$0 } ?? 0; let dispatch = now-frame
    maxGap = max(maxGap,gap); maxFrameDispatch = max(maxFrameDispatch,dispatch)
    if let fault = ReactionCore.frameFault(gap: gap, dispatch: dispatch) { stop(fault); return }
    lastFrame = frame; lastCallbackMs = now
    if nextTrial < trials.count && estimate >= Double(trials[nextTrial].plannedOnsetMs) {
      let lateness = estimate-Double(trials[nextTrial].plannedOnsetMs)
      if let fault = ReactionCore.frameFault(gap: 0, dispatch: 0, lateness: lateness) { stop(fault); return }
      trials[nextTrial].frameTimestampMs = frame-startMs; trials[nextTrial].callbackTimestampMs = relative; trials[nextTrial].onsetMs = estimate
      visibleStimulus = trials[nextTrial].stimulus
      let phase = trials[nextTrial].phase; nextTrial += 1
      if nextTrial == trials.count { terminalCutoff = estimate+ReactionConfig.windowMs+ReactionConfig.drainMs }
      onProgress(["runId":runId,"workspaceEpoch":epoch,"phase":phase,"presented":nextTrial,"total":66]); setNeedsDisplay()
    } else if nextTrial > 0, let onset = trials[nextTrial-1].onsetMs, estimate >= onset+ReactionConfig.windowMs, visibleStimulus != nil {
      visibleStimulus = nil; setNeedsDisplay()
    }
  }
  override func touchesBegan(_ touches: Set<UITouch>, with event: UIEvent?) { receive(touches, event: event) }
  override func touchesEnded(_ touches: Set<UITouch>, with event: UIEvent?) { release(touches) }
  override func touchesCancelled(_ touches: Set<UITouch>, with event: UIEvent?) { stop("INPUT_CANCELED"); release(touches) }
  fileprivate func receive(_ suppliedTouches: Set<UITouch>, event: UIEvent?) {
    guard active else { return }
    // UIKit dispatches one native event to multiple controls. Inspect its complete began batch once;
    // an End-task touch in that batch cancels before any response from the same batch is retained.
    let touches = (event?.allTouches ?? suppliedTouches).filter { touch in
      guard touch.phase == .began, let owner = touch.view else { return false }
      return owner === self || owner.isDescendant(of: self)
    }

    if touches.contains(where: { endRect.contains($0.location(in: self)) }) { stop("USER_CANCELED"); return }
    let dispatch = clockMs()-startMs
    if ReactionCore.inputAdmission(retainedCount: inputs.count, dispatchMs: dispatch, terminalCutoffMs: terminalCutoff) == "ignore_after_terminal" { return }
    let ordered = touches.sorted { a,b in
      let pa = a.location(in: self), pb = b.location(in: self)
      let ra = ReactionCore.rank(target(pa)), rb = ReactionCore.rank(target(pb))
      if ra != rb { return ra < rb }; if pa.x != pb.x { return pa.x < pb.x }; return pa.y < pb.y
    }
    for touch in ordered {
      let id = ObjectIdentifier(touch)
      if pointerIds[id] != nil { continue }
      guard ReactionCore.inputAdmission(retainedCount: inputs.count, dispatchMs: dispatch, terminalCutoffMs: terminalCutoff) != "overflow" else { overflowCount += 1; stop("INPUT_BUFFER_OVERFLOW"); return }
      pointerIds[id] = nextPointerId; nextPointerId += 1
      let input = ReactionInput(nativeTimestampMs: touch.timestamp*1000-startMs, dispatchTimestampMs: dispatch,
        target: target(touch.location(in:self)), pointerId: pointerIds[id]!, nativeSequence: inputs.count,
        inputKind: touch.type == .direct ? "direct_touch" : "unsupported")
      inputs.append(input); maxInputDispatch = max(maxInputDispatch,input.dispatchDelayMs)
      if let fault = ReactionCore.inputFault(input) { stop(fault); return }
    }
  }
  fileprivate func release(_ touches: Set<UITouch>) { touches.forEach { pointerIds.removeValue(forKey: ObjectIdentifier($0)) } }
  private func target(_ point: CGPoint) -> String { leftRect.contains(point) ? "left" : (rightRect.contains(point) ? "right" : "outside") }
  func cancel(runId requested: String, reason: String) throws -> [String: Any] {
    guard requested == runId || (!active && requested == requestedRunId) else { throw NSError(domain:"OTGDReactionTask",code:1,userInfo:[NSLocalizedDescriptionKey:"RUN_ID_MISMATCH"]) }
    if !active && !seenRuns.contains(requested) {
      guard requested == requestedRunId, UUID(uuidString: requested) != nil,
        requestedSeed.isFinite, requestedSeed >= 0, requestedSeed <= Double(UInt32.max), requestedSeed.rounded(.towardZero) == requestedSeed,
        !requestedEpoch.isEmpty, requestedEpoch.count <= 128, seenRuns.count < 128 else {
        throw NSError(domain: "OTGDReactionTask", code: 2, userInfo: [NSLocalizedDescriptionKey: "INVALID_PENDING_RUN"])
      }
      initializeRun()
    }
    requestedRunning = false
    guard active else { return cancelReceipt(runId: requested, status: "already_terminal") }
    let permitted = ["USER_CANCELED","ROUTE_HIDDEN","WORKSPACE_CHANGED","WITHDRAWAL","BACKGROUND","FOCUS_LOST","VIEW_DETACHED","LAYOUT_CHANGED"]
    stop(permitted.contains(reason) ? reason : "USER_CANCELED")
    return cancelReceipt(runId: requested, status: "stopped")
  }
  private func cancelReceipt(runId requested: String, status: String) -> [String: Any] {
    var receipt: [String: Any] = ["runId": requested, "status": status]
    if let result = terminalResult, result["runId"] as? String == requested { receipt["result"] = result }
    return receipt
  }
  func stop(_ reason: String) {
    guard active else { return }
    terminalLatch.requestCancel(reason)
    if !flags.contains(reason) { flags.append(reason) }; complete(validRequested:false,duration:clockMs()-startMs)
  }
  private func finishAtCutoff() {
    guard let cutoff = terminalCutoff else { return }
    guard let last = lastFrame, startMs+cutoff-last <= ReactionConfig.budgetMs else { stop("FRAME_GAP_EXCEEDED"); return }
    complete(validRequested:true,duration:cutoff)
  }
  private func complete(validRequested: Bool, duration: Double) {
    guard active, let latchedValid = terminalLatch.commit(validRequested) else { return }
    active = false; displayLink?.invalidate(); displayLink = nil; watchdog?.cancel(); watchdog = nil
    callObserver.setDelegate(nil,queue:nil); visibleStimulus=nil; setNeedsDisplay()
    let valid = latchedValid && nextTrial == 66 && flags.allSatisfy { $0 == "UNCALIBRATED_TIMING" }
    let evidence = ReactionCore.score(trials:trials,inputs:inputs,endedMs:duration,intact:valid)
    if valid && evidence.counts["correctGo"] == 0 { flags.append("NO_CORRECT_GO_RESPONSES") }
    let observed = Date(); let screen = window?.screen ?? UIScreen.main; let scale = screen.scale
    #if targetEnvironment(simulator)
    let simulator = true
    #else
    let simulator = false
    #endif
    var info = utsname(); uname(&info)
    let physicalModel = withUnsafeBytes(of: &info.machine) { bytes in String(cString:bytes.baseAddress!.assumingMemoryBound(to:CChar.self)) }
    let model = ProcessInfo.processInfo.environment["SIMULATOR_MODEL_IDENTIFIER"] ?? physicalModel
    let timing: [String: Any] = [
      "clockDomain":"ios_uptime","inputTimestampMethod":"uitouch_timestamp","inputTimestampResolutionMs":NSNull(),
      "presentationEvidenceMethod":"cadisplaylink_target_timestamp","calibrationStatus":"uncalibrated","physicalOnsetVerified":false,
      "modelEligible":false,"simulator":simulator,"deviceModel":String(model.prefix(96)),"osVersion":String(UIDevice.current.systemVersion.prefix(64)),
      "nativeBuild":"1.0.0","viewWidthPoints":Double(frozenBounds.width),"viewHeightPoints":Double(frozenBounds.height),
      "viewWidthPixels":Double(frozenBounds.width*scale),"viewHeightPixels":Double(frozenBounds.height*scale),"pixelDensity":Double(scale),
      "orientation":"portrait","fontFamily":UIFont.systemFont(ofSize:20,weight:.regular).fontName,"textScale":1,
      "nominalRefreshHz":Double(screen.maximumFramesPerSecond),"maxObservedFrameGapMs":maxGap,"maxObservedFrameDispatchMs":maxFrameDispatch,
      "maxObservedInputDispatchMs":maxInputDispatch,"terminalCutoffMs":nullValue(terminalCutoff),"finalDrainMs":100,"overflowTriggerCount":overflowCount,
      "utcAnchorMethod":"start_utc_plus_monotonic_elapsed","observedEndedAt":utc(observed),
      "observedWallClockDeltaMs":observed.timeIntervalSince(startWall)*1000-duration,"physicalLuminance":"unmeasured"]
    let result: [String: Any] = ["schemaVersion":"1.0.0","taskVersion":"choice_inhibit_v0","implementationVersion":"1.0.0",
      "extractorVersion":"choice_inhibit_features_1","status":valid ? "valid" : "invalid","source":"native_task","platform":"ios",
      "runId":runId,"workspaceEpoch":epoch,"seed":Int64(seed),"configurationId":ReactionConfig.id,"configurationSha256":ReactionConfig.sha256,
      "scheduleSha256":ReactionCore.scheduleHash(seed:seed,trials:trials),"startedAt":utc(startWall),"endedAt":utc(startWall.addingTimeInterval(duration/1000)),
      "nativeStartMs":startMs,"nativeEndMs":startMs+duration,"durationMs":duration,"trialEvents":evidence.trials.map { $0.dictionary() },
      "inputEvents":evidence.inputs.map { $0.dictionary() },"counts":evidence.counts,"features":nullValue(evidence.features),"qualityFlags":flags,"timing":timing]
    // Freeze before emitting: cancel can return the identical evidence if bridge event delivery is delayed.
    terminalResult = result
    onComplete(result)
  }
  override func draw(_ rect: CGRect) {
    super.draw(rect)
    let area = self.rect(200,150,600,400); let side = min(area.width,area.height)
    let origin = CGPoint(x:area.midX-side/2,y:area.midY-side/2)
    UIColor.white.setFill()
    switch visibleStimulus {
    case "left", "right":
      let polygon: [(CGFloat,CGFloat)] = [(150,400),(550,400),(550,200),(850,500),(550,800),(550,600),(150,600)]
      let path = UIBezierPath()
      for (i,p) in polygon.enumerated() {
        let x = visibleStimulus == "left" ? 1000-p.0 : p.0
        let point = CGPoint(x:origin.x+side*x/1000,y:origin.y+side*p.1/1000)
        if i == 0 { path.move(to:point) } else { path.addLine(to:point) }
      }; path.close(); path.fill()
    case "no_go":
      let attributes: [NSAttributedString.Key: Any] = [.font:UIFont.systemFont(ofSize:32,weight:.regular),.foregroundColor:UIColor.white]
      let label = "WAIT" as NSString; let size=label.size(withAttributes:attributes)
      label.draw(at:CGPoint(x:area.midX-size.width/2,y:area.midY-size.height/2),withAttributes:attributes)
    default:
      color(0xB8C4CE).setFill(); UIBezierPath(ovalIn:CGRect(x:area.midX-4,y:area.midY-4,width:8,height:8)).fill()
    }
  }
  private func color(_ hex: UInt32) -> UIColor { UIColor(red:CGFloat((hex>>16)&255)/255,green:CGFloat((hex>>8)&255)/255,blue:CGFloat(hex&255)/255,alpha:1) }
  private func clockMs() -> Double { CACurrentMediaTime()*1000 }
  private func utc(_ date: Date) -> String { let f=ISO8601DateFormatter(); f.formatOptions=[.withInternetDateTime,.withFractionalSeconds]; return f.string(from:date) }
}
