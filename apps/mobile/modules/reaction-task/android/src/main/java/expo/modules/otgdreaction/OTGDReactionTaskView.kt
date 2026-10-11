package expo.modules.otgdreaction

import android.content.Context
import android.graphics.Canvas
import android.graphics.Color
import android.graphics.Paint
import android.graphics.Path
import android.graphics.RectF
import android.graphics.Typeface
import android.graphics.drawable.GradientDrawable
import android.media.AudioManager
import android.os.Build
import android.os.Handler
import android.os.Looper
import android.util.TypedValue
import android.view.Choreographer
import android.view.InputDevice
import android.view.MotionEvent
import android.view.View
import android.view.accessibility.AccessibilityManager
import android.widget.Button
import expo.modules.kotlin.AppContext
import expo.modules.kotlin.viewevent.EventDispatcher
import expo.modules.kotlin.views.ExpoView
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import java.util.TimeZone
import java.util.WeakHashMap
import kotlin.math.abs
import kotlin.math.min

internal object ReactionViewRegistry {
  private val views = WeakHashMap<OTGDReactionTaskView, Boolean>()
  fun add(view: OTGDReactionTaskView) { views[view] = true }
  fun stopAll(reason: String) {
    val stop = Runnable { views.keys.toList().forEach { it.stop(reason) } }
    if (Looper.myLooper() == Looper.getMainLooper()) stop.run() else Handler(Looper.getMainLooper()).post(stop)
  }
}

class OTGDReactionTaskView(context: Context, appContext: AppContext) : ExpoView(context, appContext), Choreographer.FrameCallback {
  val onProgress by EventDispatcher()
  // The generic Expo 57 overload accepts nullable map values. ViewEvent uses
  // JSTypeConverterProvider's map conversion, whose putGeneric(null) calls
  // WritableMap.putNull; nested maps/lists take the same conversion path.
  // Keep absent features/timestamps explicit rather than filtering or casting.
  val onComplete by EventDispatcher<Map<String, Any?>>()
  var requestedRunId = ""
  var requestedSeed = 0.0
  var requestedRunning = false
  var requestedConfigurationId = ""
  var requestedConfigurationHash = ""
  var requestedEpoch = ""
  private val handler = Handler(Looper.getMainLooper())
  private val paint = Paint(Paint.ANTI_ALIAS_FLAG)
  private val density = resources.displayMetrics.density.toDouble()
  private val left = button("Left", 20f, "#213547")
  private val right = button("Right", 20f, "#213547")
  private val end = button("End task", 16f, "#334155")
  private var active = false
  private var runId = ""
  private var epoch = ""
  private var seed = 0L
  private var startMs = 0.0
  private var startWallMs = 0L
  private var frozenWidth = 0
  private var frozenHeight = 0
  private var nextTrial = 0
  private var visibleStimulus: String? = null
  private var trials = emptyList<Trial>()
  private val inputs = mutableListOf<TaskInput>()
  private val seenRuns = mutableSetOf<String>()
  private var lastFrame: Double? = null
  private var lastCallbackMs = 0.0
  private var maxGap = 0.0
  private var maxFrameDispatch = 0.0
  private var maxInputDispatch = 0.0
  private var overflowCount = 0
  private val flags = linkedSetOf<String>()
  private var terminalCutoff: Double? = null
  private var terminalLatch = ReactionTerminalLatch()
  private var terminalResult: Map<String, Any?>? = null
  private val watchdog = object : Runnable {
    override fun run() {
      if (!active) return
      val now = clockMs()
      val cutoff = terminalCutoff
      if (cutoff != null && now - startMs >= cutoff) { finishAtCutoff(); return }
      if (now - lastCallbackMs > ReactionConfig.BUDGET_MS) { stop("FRAME_CALLBACK_DELAY_EXCEEDED"); return }
      if (nextTrial < trials.size && now - startMs > trials[nextTrial].plannedOnsetMs + ReactionConfig.BUDGET_MS) { stop("SCHEDULED_ONSET_LATE"); return }
      handler.postDelayed(this, 20)
    }
  }

  init {
    setWillNotDraw(false); clipChildren = true; isMotionEventSplittingEnabled = false
    setBackgroundColor(Color.parseColor("#101820"))
    addView(left); addView(right); addView(end)
    end.setOnClickListener { stop("USER_CANCELED") }
    isFocusable = true
    ReactionViewRegistry.add(this)
  }
  private fun button(label: String, points: Float, fill: String): Button = Button(context).apply {
    text = label; contentDescription = label; isAllCaps = false
    setTextColor(Color.WHITE); setTextSize(TypedValue.COMPLEX_UNIT_DIP, points)
    typeface = Typeface.create("sans-serif", Typeface.NORMAL); includeFontPadding = false
    maxLines = 2; setPadding(0, 0, 0, 0); minWidth = 0; minHeight = 0; minimumWidth = 0; minimumHeight = 0
    isHapticFeedbackEnabled = false; isSoundEffectsEnabled = false; stateListAnimator = null
    background = GradientDrawable().apply {
      setColor(Color.parseColor(fill)); cornerRadius = (12 * density).toFloat()
      setStroke((2 * density).toInt(), Color.parseColor("#71899E"))
    }
  }
  private fun rect(x: Int, y: Int, w: Int, h: Int) = RectF(width*x/1000f, height*y/1000f, width*(x+w)/1000f, height*(y+h)/1000f)
  private fun leftRect() = rect(20,650,460,250)
  private fun rightRect() = rect(520,650,460,250)
  private fun endRect() = rect(750,20,230,120)
  private fun layoutControl(view: View, bounds: RectF) {
    view.measure(MeasureSpec.makeMeasureSpec(bounds.width().toInt(), MeasureSpec.EXACTLY), MeasureSpec.makeMeasureSpec(bounds.height().toInt(), MeasureSpec.EXACTLY))
    view.layout(bounds.left.toInt(), bounds.top.toInt(), bounds.right.toInt(), bounds.bottom.toInt())
  }
  override fun onLayout(changed: Boolean, l: Int, t: Int, r: Int, b: Int) {
    if (active && (width != frozenWidth || height != frozenHeight)) stop("LAYOUT_CHANGED")
    layoutControl(left, leftRect()); layoutControl(right, rightRect()); layoutControl(end, endRect())
    commitProps()
  }
  override fun onAttachedToWindow() { super.onAttachedToWindow(); commitProps() }
  override fun onDetachedFromWindow() { stop("VIEW_DETACHED"); super.onDetachedFromWindow() }
  override fun onWindowFocusChanged(hasWindowFocus: Boolean) {
    super.onWindowFocusChanged(hasWindowFocus)
    if (!hasWindowFocus) stop("FOCUS_LOST") else commitProps()
  }
  override fun onWindowVisibilityChanged(visibility: Int) { super.onWindowVisibilityChanged(visibility); if (visibility != VISIBLE) stop("BACKGROUND") }

  fun commitProps() {
    if (active && (!requestedRunning || requestedRunId != runId || requestedEpoch != epoch || requestedSeed != seed.toDouble()
        || requestedConfigurationId != ReactionConfig.ID || requestedConfigurationHash != ReactionConfig.SHA256)) {
      stop(if (requestedEpoch != epoch) "WORKSPACE_CHANGED" else "USER_CANCELED")
    }
    if (!requestedRunning || active || seenRuns.contains(requestedRunId) || !isAttachedToWindow || width == 0 || height == 0 || !hasWindowFocus()) return
    require(requestedRunId.matches(Regex("^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"))) { "RUN_ID_INVALID" }
    require(requestedEpoch.isNotBlank() && requestedEpoch.length <= 128) { "WORKSPACE_EPOCH_INVALID" }
    require(requestedSeed.isFinite() && requestedSeed >= 0 && requestedSeed <= 4294967295.0 && requestedSeed % 1.0 == 0.0) { "SEED_OUT_OF_RANGE" }
    require(seenRuns.size < 128) { "VIEW_RUN_LIMIT_REACHED" }
    initializeRun()
    if (requestedConfigurationId != ReactionConfig.ID || requestedConfigurationHash != ReactionConfig.SHA256) { stop("CONFIGURATION_MISMATCH"); return }
    if (width / density < 240 || height / density < 400 || width > height) { stop("LAYOUT_UNSUPPORTED"); return }
    if (isTouchExplorationEnabled()) { stop("INPUT_MODE_UNSUPPORTED"); return }
    if (callActive()) { stop("CALL_INTERRUPTION"); return }
    invalidate(); Choreographer.getInstance().postFrameCallback(this); handler.postDelayed(watchdog, 20)
  }
  private fun initializeRun() {
    runId = requestedRunId; epoch = requestedEpoch; seed = requestedSeed.toLong(); seenRuns.add(runId)
    startMs = clockMs(); startWallMs = System.currentTimeMillis(); frozenWidth = width; frozenHeight = height
    trials = ReactionCore.schedule(seed); inputs.clear(); flags.clear(); flags.add("UNCALIBRATED_TIMING")
    nextTrial = 0; visibleStimulus = null; terminalCutoff = null; terminalResult = null; lastFrame = null; lastCallbackMs = startMs
    maxGap = 0.0; maxFrameDispatch = 0.0; maxInputDispatch = 0.0; overflowCount = 0; active = true; terminalLatch = ReactionTerminalLatch()
  }
  private fun isTouchExplorationEnabled() = (context.getSystemService(Context.ACCESSIBILITY_SERVICE) as AccessibilityManager).isTouchExplorationEnabled
  private fun callActive(): Boolean {
    val mode = (context.getSystemService(Context.AUDIO_SERVICE) as AudioManager).mode
    return mode == AudioManager.MODE_IN_CALL || mode == AudioManager.MODE_IN_COMMUNICATION
  }
  override fun doFrame(frameTimeNanos: Long) {
    if (!active) return
    val now = clockMs(); val relative = now - startMs
    if (terminalCutoff?.let { relative >= it } == true) { finishAtCutoff(); return }
    if (!hasWindowFocus() || windowVisibility != VISIBLE || !isShown) { stop("FOCUS_LOST"); return }
    if (isTouchExplorationEnabled()) { stop("INPUT_MODE_UNSUPPORTED"); return }
    if (callActive()) { stop("CALL_INTERRUPTION"); return }
    val frame = frameTimeNanos / 1e6; val gap = lastFrame?.let { frame - it } ?: 0.0; val dispatch = now - frame
    maxGap = maxOf(maxGap, gap); maxFrameDispatch = maxOf(maxFrameDispatch, dispatch)
    ReactionCore.frameFault(gap, dispatch)?.let { stop(it); return }
    lastFrame = frame; lastCallbackMs = now
    val estimate = frame - startMs
    if (nextTrial < trials.size && estimate >= trials[nextTrial].plannedOnsetMs) {
      val trial = trials[nextTrial]
      ReactionCore.frameFault(0.0, 0.0, estimate - trial.plannedOnsetMs)?.let { stop(it); return }
      trial.frameTimestampMs = estimate; trial.callbackTimestampMs = relative; trial.onsetMs = estimate
      visibleStimulus = trial.stimulus; nextTrial++
      if (nextTrial == trials.size) terminalCutoff = estimate + ReactionConfig.WINDOW_MS + ReactionConfig.DRAIN_MS
      onProgress(mapOf("runId" to runId, "workspaceEpoch" to epoch, "phase" to trial.phase, "presented" to nextTrial, "total" to 66))
      invalidate()
    } else if (nextTrial > 0 && estimate >= trials[nextTrial - 1].onsetMs!! + ReactionConfig.WINDOW_MS && visibleStimulus != null) {
      visibleStimulus = null; invalidate()
    }
    if (active) Choreographer.getInstance().postFrameCallback(this)
  }
  override fun dispatchTouchEvent(event: MotionEvent): Boolean {
    if (active && event.actionMasked == MotionEvent.ACTION_CANCEL) { stop("INPUT_CANCELED"); return true }
    if (active && (event.actionMasked == MotionEvent.ACTION_DOWN || event.actionMasked == MotionEvent.ACTION_POINTER_DOWN)) {
      val i = event.actionIndex; val x = event.getX(i); val y = event.getY(i)
      if (endRect().contains(x,y)) { stop("USER_CANCELED"); return true }
      val now = clockMs(); val relative = now - startMs
      val admission = ReactionCore.inputAdmission(inputs.size, relative, terminalCutoff)
      if (admission != "ignore_after_terminal") {
        if (admission == "overflow") { overflowCount++; stop("INPUT_BUFFER_OVERFLOW"); return true }
        val stamp = if (Build.VERSION.SDK_INT >= 34) event.eventTimeNanos / 1e6 else event.eventTime.toDouble()
        val side = when { leftRect().contains(x,y) -> "left"; rightRect().contains(x,y) -> "right"; else -> "outside" }
        val direct = event.isFromSource(InputDevice.SOURCE_TOUCHSCREEN) && event.getToolType(i) == MotionEvent.TOOL_TYPE_FINGER
        val input = TaskInput(stamp - startMs, relative, side, event.getPointerId(i), inputs.size, if (direct) "direct_touch" else "unsupported")
        inputs.add(input); maxInputDispatch = maxOf(maxInputDispatch, input.dispatchDelayMs)
        ReactionCore.inputFault(input)?.let { stop(it); return true }
      }
    }
    return super.dispatchTouchEvent(event)
  }
  override fun onTouchEvent(event: MotionEvent): Boolean = true
  fun cancel(requestedId: String, reason: String): Map<String, Any?> {
    require(requestedId == runId || (!active && requestedId == requestedRunId)) { "RUN_ID_MISMATCH" }
    if (!active && !seenRuns.contains(requestedId)) {
      require(requestedId == requestedRunId && requestedSeed.isFinite() && requestedSeed in 0.0..4294967295.0 && requestedSeed % 1.0 == 0.0 && requestedEpoch.isNotBlank() && seenRuns.size < 128) { "INVALID_PENDING_RUN" }
      // A Back event can precede attachment or the first layout. It still seals this run and emits invalid evidence.
      initializeRun()
    }
    requestedRunning = false
    if (!active) return cancelReceipt(requestedId, "already_terminal")
    val permitted = setOf("USER_CANCELED","ROUTE_HIDDEN","WORKSPACE_CHANGED","WITHDRAWAL","BACKGROUND","FOCUS_LOST","VIEW_DETACHED","LAYOUT_CHANGED")
    stop(if (reason in permitted) reason else "USER_CANCELED")
    return cancelReceipt(requestedId, "stopped")
  }
  private fun cancelReceipt(requestedId: String, status: String): Map<String, Any?> = linkedMapOf<String, Any?>("runId" to requestedId, "status" to status).apply {
    terminalResult?.takeIf { it["runId"] == requestedId }?.let { put("result", it) }
  }
  fun stop(reason: String) { if (active) { terminalLatch.requestCancel(reason); flags.add(reason); complete(false, clockMs() - startMs) } }
  private fun finishAtCutoff() {
    val cutoff = terminalCutoff ?: return
    if (lastFrame == null || startMs + cutoff - lastFrame!! > ReactionConfig.BUDGET_MS) { stop("FRAME_GAP_EXCEEDED"); return }
    complete(true, cutoff)
  }
  private fun complete(requestedValid: Boolean, duration: Double) {
    if (!active) return
    val latchedValid = terminalLatch.commit(requestedValid) ?: return
    active = false; Choreographer.getInstance().removeFrameCallback(this); handler.removeCallbacks(watchdog)
    visibleStimulus = null; invalidate()
    val valid = latchedValid && nextTrial == 66 && flags.all { it == "UNCALIBRATED_TIMING" }
    val evidence = ReactionCore.score(trials, inputs, duration, valid)
    if (valid && evidence.counts["correctGo"] == 0) flags.add("NO_CORRECT_GO_RESPONSES")
    val observedWall = System.currentTimeMillis()
    val model = "${Build.MANUFACTURER} ${Build.MODEL}".take(96)
    val timing = linkedMapOf<String, Any?>(
      "clockDomain" to "android_uptime", "inputTimestampMethod" to if (Build.VERSION.SDK_INT >= 34) "motion_event_uptime_nanos" else "motion_event_uptime_ms",
      "inputTimestampResolutionMs" to if (Build.VERSION.SDK_INT >= 34) 0.000001 else 1.0,
      "presentationEvidenceMethod" to "choreographer_frame_time_nanos", "calibrationStatus" to "uncalibrated", "physicalOnsetVerified" to false,
      "modelEligible" to false, "simulator" to (Build.FINGERPRINT.contains("generic") || Build.MODEL.contains("Emulator") || Build.MODEL.contains("sdk_gphone")),
      "deviceModel" to model, "osVersion" to Build.VERSION.RELEASE.take(64), "nativeBuild" to "1.0.0", "viewWidthPoints" to frozenWidth/density,
      "viewHeightPoints" to frozenHeight/density, "viewWidthPixels" to frozenWidth, "viewHeightPixels" to frozenHeight, "pixelDensity" to density,
      "orientation" to "portrait", "fontFamily" to "sans-serif", "textScale" to 1, "nominalRefreshHz" to (display?.refreshRate?.toDouble() ?: 0.0),
      "maxObservedFrameGapMs" to maxGap, "maxObservedFrameDispatchMs" to maxFrameDispatch, "maxObservedInputDispatchMs" to maxInputDispatch,
      "terminalCutoffMs" to terminalCutoff, "finalDrainMs" to 100, "overflowTriggerCount" to overflowCount,
      "utcAnchorMethod" to "start_utc_plus_monotonic_elapsed", "observedEndedAt" to utc(observedWall),
      "observedWallClockDeltaMs" to (observedWall - startWallMs - duration), "physicalLuminance" to "unmeasured")
    val result = linkedMapOf<String, Any?>("schemaVersion" to "1.0.0", "taskVersion" to "choice_inhibit_v0", "implementationVersion" to "1.0.0",
      "extractorVersion" to "choice_inhibit_features_1", "status" to if (valid) "valid" else "invalid", "source" to "native_task", "platform" to "android",
      "runId" to runId, "workspaceEpoch" to epoch, "seed" to seed, "configurationId" to ReactionConfig.ID, "configurationSha256" to ReactionConfig.SHA256,
      "scheduleSha256" to ReactionCore.scheduleHash(seed,trials), "startedAt" to utc(startWallMs), "endedAt" to utc(startWallMs+duration.toLong()),
      "nativeStartMs" to startMs, "nativeEndMs" to startMs+duration, "durationMs" to duration,
      "trialEvents" to evidence.trials.map { it.map() }, "inputEvents" to evidence.inputs.map { it.map() },
      "counts" to evidence.counts, "features" to evidence.features, "qualityFlags" to flags.toList(), "timing" to timing)
    // Freeze before emitting: cancel can return the identical evidence if bridge event delivery is delayed.
    terminalResult = result
    onComplete(result)
  }
  override fun onDraw(canvas: Canvas) {
    super.onDraw(canvas)
    val area = rect(200,150,600,400); val side = min(area.width(),area.height()); val ox = area.centerX()-side/2; val oy = area.centerY()-side/2
    paint.color = Color.WHITE; paint.style = Paint.Style.FILL
    when (visibleStimulus) {
      "left", "right" -> {
        val points = arrayOf(150 to 400,550 to 400,550 to 200,850 to 500,550 to 800,550 to 600,150 to 600)
        val path = Path()
        points.forEachIndexed { index, pair ->
          val x = ox + side*(if (visibleStimulus=="left") 1000-pair.first else pair.first)/1000f
          val y = oy + side*pair.second/1000f
          if (index==0) path.moveTo(x,y) else path.lineTo(x,y)
        }
        path.close(); canvas.drawPath(path,paint)
      }
      "no_go" -> {
        paint.textSize=(32*density).toFloat(); paint.typeface=Typeface.create("sans-serif",Typeface.NORMAL); paint.textAlign=Paint.Align.CENTER
        canvas.drawText("WAIT",area.centerX(),area.centerY()-(paint.ascent()+paint.descent())/2,paint)
      }
      else -> { paint.color=Color.parseColor("#B8C4CE"); canvas.drawCircle(area.centerX(),area.centerY(),(4*density).toFloat(),paint) }
    }
  }
  private fun clockMs() = System.nanoTime()/1e6
  private fun utc(milliseconds: Long) = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss.SSS'Z'", Locale.US).apply { timeZone=TimeZone.getTimeZone("UTC") }.format(Date(milliseconds))
}
