package expo.modules.otgdreaction

import java.security.MessageDigest
import kotlin.math.floor

/** Deterministic extraction only. Native view owns clocks, lifecycle and presentation. */
object ReactionConfig {
  const val ID = "choice_inhibit_v0_native_dev_1"
  const val SHA256 = "61bd03244a9f82fdc5a1a2b6658483ca201ab5d39a95e64cde0d00f1d5a666c3"
  const val WINDOW_MS = 1000.0
  const val DRAIN_MS = 100.0
  const val BUDGET_MS = 100.0
  const val INPUT_LIMIT = 1024
  const val VERSION = "1.0.0"
}

data class Trial(
  val index: Int, val phase: String, val stimulus: String, val plannedOnsetMs: Int, val onsetIntervalMs: Int,
  var frameTimestampMs: Double? = null, var callbackTimestampMs: Double? = null, var onsetMs: Double? = null,
  var outcome: String = "unresolved", var selectedInputSequence: Int? = null,
  var responseTimeMs: Double? = null, var correctGoRtMs: Double? = null
) {
  fun map(): Map<String, Any?> = linkedMapOf(
    "index" to index, "phase" to phase, "stimulus" to stimulus, "plannedOnsetMs" to plannedOnsetMs,
    "onsetIntervalMs" to onsetIntervalMs, "presented" to (onsetMs != null),
    "frameTimestampMs" to frameTimestampMs, "callbackTimestampMs" to callbackTimestampMs,
    "onsetMs" to onsetMs, "onsetLatenessMs" to onsetMs?.minus(plannedOnsetMs), "outcome" to outcome,
    "selectedInputSequence" to selectedInputSequence, "responseTimeMs" to responseTimeMs, "correctGoRtMs" to correctGoRtMs
  )
}
data class TaskInput(
  val nativeTimestampMs: Double, val dispatchTimestampMs: Double, val target: String,
  val pointerId: Int, val nativeSequence: Int, val inputKind: String = "direct_touch",
  var disposition: String = "anticipatory", var trialIndex: Int? = null, var anticipatoryForTrialIndex: Int? = null
) {
  val dispatchDelayMs: Double get() = dispatchTimestampMs - nativeTimestampMs
  fun map(): Map<String, Any?> = linkedMapOf(
    "nativeTimestampMs" to nativeTimestampMs, "dispatchTimestampMs" to dispatchTimestampMs,
    "dispatchDelayMs" to dispatchDelayMs, "target" to target, "pointerId" to pointerId,
    "nativeSequence" to nativeSequence, "inputKind" to inputKind, "disposition" to disposition,
    "trialIndex" to trialIndex, "anticipatoryForTrialIndex" to anticipatoryForTrialIndex
  )
}
data class ScoredEvidence(val trials: List<Trial>, val inputs: List<TaskInput>, val counts: Map<String, Int>, val features: Map<String, Any?>?)

object ReactionCore {
  fun inputAdmission(retainedCount: Int, dispatchMs: Double, terminalCutoffMs: Double?): String = when {
    terminalCutoffMs != null && dispatchMs >= terminalCutoffMs -> "ignore_after_terminal"
    retainedCount >= ReactionConfig.INPUT_LIMIT -> "overflow"
    else -> "accept"
  }
  fun schedule(seed: Long): List<Trial> {
    require(seed in 0..0xffffffffL) { "SEED_OUT_OF_RANGE" }
    var state = seed
    fun next(): Long { state = (1664525L * state + 1013904223L) and 0xffffffffL; return state }
    val practice = mutableListOf("left", "left", "right", "right", "no_go", "no_go")
    val scored = (List(24) { "left" } + List(24) { "right" } + List(12) { "no_go" }).toMutableList()
    for (list in listOf(practice, scored)) for (i in list.lastIndex downTo 1) {
      val j = (next() % (i + 1)).toInt(); val old = list[i]; list[i] = list[j]; list[j] = old
    }
    val gaps = List(66) { 1500 + (next() % 401).toInt() }
    var onset = 2000
    return (practice + scored).mapIndexed { i, side ->
      val trial = Trial(i, if (i < 6) "practice" else "scored", side, onset, gaps[i]); onset += gaps[i]; trial
    }
  }

  /** Exact JCS for this restricted fixed-key, safe-integer, ASCII schedule schema. */
  fun scheduleCanonical(seed: Long, trials: List<Trial>): String = buildString {
    append("{\"configuration_sha256\":\"").append(ReactionConfig.SHA256)
    append("\",\"schema_version\":\"1.0.0\",\"seed\":").append(seed).append(",\"trials\":[")
    trials.forEachIndexed { i, t ->
      if (i != 0) append(',')
      append("{\"index\":").append(t.index).append(",\"onset_interval_ms\":").append(t.onsetIntervalMs)
      append(",\"phase\":\"").append(t.phase).append("\",\"planned_onset_ms\":").append(t.plannedOnsetMs)
      append(",\"stimulus\":\"").append(t.stimulus).append("\"}")
    }
    append("]}")
  }
  fun scheduleHash(seed: Long, trials: List<Trial>): String = MessageDigest.getInstance("SHA-256")
    .digest(scheduleCanonical(seed, trials).toByteArray(Charsets.UTF_8)).joinToString("") { "%02x".format(it.toInt() and 255) }

  fun quantile(sorted: List<Double>, p: Double): Double? {
    if (sorted.isEmpty()) return null
    val index = (sorted.size - 1) * p; val lo = floor(index).toInt(); val hi = minOf(lo + 1, sorted.lastIndex)
    return sorted[lo] + (sorted[hi] - sorted[lo]) * (index - lo)
  }
  private fun rank(target: String) = when (target) { "left" -> 0; "right" -> 1; else -> 2 }
  fun inputFault(input: TaskInput): String? = when {
    !input.nativeTimestampMs.isFinite() || !input.dispatchTimestampMs.isFinite() || input.dispatchDelayMs < 0 -> "NATIVE_CLOCK_INCONSISTENCY"
    input.inputKind != "direct_touch" -> "INPUT_MODE_UNSUPPORTED"
    input.dispatchDelayMs > ReactionConfig.BUDGET_MS -> "INPUT_DISPATCH_DELAY_EXCEEDED"
    else -> null
  }
  fun frameFault(gap: Double, dispatch: Double, lateness: Double? = null): String? = when {
    !gap.isFinite() || !dispatch.isFinite() || gap < 0 || dispatch < 0 -> "NATIVE_CLOCK_INCONSISTENCY"
    gap > ReactionConfig.BUDGET_MS -> "FRAME_GAP_EXCEEDED"
    dispatch > ReactionConfig.BUDGET_MS -> "FRAME_CALLBACK_DELAY_EXCEEDED"
    lateness != null && (!lateness.isFinite() || lateness < 0) -> "NATIVE_CLOCK_INCONSISTENCY"
    lateness != null && lateness > ReactionConfig.BUDGET_MS -> "SCHEDULED_ONSET_LATE"
    else -> null
  }

  fun score(trials: List<Trial>, rawInputs: List<TaskInput>, endedMs: Double, intact: Boolean): ScoredEvidence {
    val inputs = rawInputs.sortedWith(compareBy<TaskInput> { it.nativeTimestampMs }.thenBy { rank(it.target) }
      .thenBy { it.pointerId }.thenBy { it.nativeSequence })
    val presented = trials.filter { it.onsetMs != null }
    val selected = mutableMapOf<Int, TaskInput>()
    for (t in trials) { t.outcome = "unresolved"; t.selectedInputSequence = null; t.responseTimeMs = null; t.correctGoRtMs = null }
    for (input in inputs) {
      input.trialIndex = null; input.anticipatoryForTrialIndex = null
      val trial = presented.firstOrNull { input.nativeTimestampMs >= it.onsetMs!! && input.nativeTimestampMs < it.onsetMs!! + ReactionConfig.WINDOW_MS }
      input.trialIndex = trial?.index
      if (inputFault(input) != null) { input.disposition = if (input.inputKind != "direct_touch") "unsupported" else "timing_fault"; continue }
      if (input.target == "outside") { input.disposition = "outside"; continue }
      if (trial == null) {
        val previous = presented.lastOrNull { input.nativeTimestampMs >= it.onsetMs!! + ReactionConfig.WINDOW_MS }
        val following = presented.firstOrNull { input.nativeTimestampMs < it.onsetMs!! }
        input.trialIndex = previous?.index; input.anticipatoryForTrialIndex = following?.index
        input.disposition = if (previous == null) "anticipatory" else "late"
      } else if (selected.containsKey(trial.index)) input.disposition = "additional_response"
      else { selected[trial.index] = input; input.disposition = "selected" }
    }
    for (trial in presented) {
      val response = selected[trial.index]
      if (response != null) {
        trial.selectedInputSequence = response.nativeSequence; trial.responseTimeMs = response.nativeTimestampMs - trial.onsetMs!!
        trial.outcome = when { trial.stimulus == "no_go" -> "commission"; response.target == trial.stimulus -> "correct"; else -> "wrong_choice" }
        if (trial.outcome == "correct") trial.correctGoRtMs = trial.responseTimeMs
      } else if (endedMs >= trial.onsetMs!! + ReactionConfig.WINDOW_MS) trial.outcome = if (trial.stimulus == "no_go") "correct_withhold" else "omission"
    }
    val scored = presented.filter { it.phase == "scored" }; val go = scored.filter { it.stimulus != "no_go" }; val noGo = scored.filter { it.stimulus == "no_go" }
    val correct = go.count { it.outcome == "correct" }; val omissions = go.count { it.outcome == "omission" }
    val wrong = go.count { it.outcome == "wrong_choice" }; val commissions = noGo.count { it.outcome == "commission" }
    val counts = linkedMapOf("presentedPractice" to presented.count { it.phase == "practice" }, "presentedScored" to scored.size,
      "presentedGo" to go.size, "presentedNoGo" to noGo.size, "completedScored" to scored.count { endedMs >= it.onsetMs!! + ReactionConfig.WINDOW_MS },
      "correctGo" to correct, "omissions" to omissions, "wrongGo" to wrong, "noGoErrors" to commissions, "correctWithholds" to noGo.count { it.outcome == "correct_withhold" })
    val rts = go.mapNotNull { it.correctGoRtMs }.sorted()
    val q25 = quantile(rts, .25); val q75 = quantile(rts, .75)
    val features = if (!intact) null else linkedMapOf<String, Any?>("medianRtMs" to quantile(rts, .5),
      "iqrRtMs" to if (q25 == null || q75 == null) null else q75 - q25, "p90RtMs" to quantile(rts, .9),
      "omissionRate" to if (go.isEmpty()) 0.0 else omissions.toDouble() / go.size,
      "wrongGoRate" to if (go.isEmpty()) 0.0 else wrong.toDouble() / go.size,
      "noGoErrorRate" to if (noGo.isEmpty()) 0.0 else commissions.toDouble() / noGo.size)
    return ScoredEvidence(trials, inputs, counts, features)
  }
}

/** Main-thread terminal latch. A pending cancellation wins and no late path can emit a second result. */
class ReactionTerminalLatch {
  var committed = false; private set
  var cancellation: String? = null; private set
  fun requestCancel(reason: String) { if (!committed && cancellation == null) cancellation = reason }
  fun commit(proposedValid: Boolean): Boolean? {
    if (committed) return null
    committed = true
    return proposedValid && cancellation == null
  }
}
