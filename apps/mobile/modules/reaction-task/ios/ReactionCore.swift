import Foundation
import CryptoKit

enum ReactionConfig {
  static let id = "choice_inhibit_v0_native_dev_1"
  static let sha256 = "61bd03244a9f82fdc5a1a2b6658483ca201ab5d39a95e64cde0d00f1d5a666c3"
  static let windowMs = 1000.0
  static let drainMs = 100.0
  static let budgetMs = 100.0
  static let inputLimit = 1024
}
final class ReactionTerminalLatch {
  private(set) var committed = false
  private(set) var cancellation: String? = nil
  func requestCancel(_ reason: String) { if !committed && cancellation == nil { cancellation = reason } }
  func commit(_ proposedValid: Bool) -> Bool? {
    guard !committed else { return nil }; committed = true
    return proposedValid && cancellation == nil
  }
}
func nullValue<T>(_ value: T?) -> Any { if let value = value { return value }; return NSNull() }

struct ReactionTrial {
  let index: Int
  let phase: String
  let stimulus: String
  let plannedOnsetMs: Int
  let onsetIntervalMs: Int
  var frameTimestampMs: Double? = nil
  var callbackTimestampMs: Double? = nil
  var onsetMs: Double? = nil
  var outcome = "unresolved"
  var selectedInputSequence: Int? = nil
  var responseTimeMs: Double? = nil
  var correctGoRtMs: Double? = nil
  func dictionary() -> [String: Any] {
    ["index": index, "phase": phase, "stimulus": stimulus, "plannedOnsetMs": plannedOnsetMs,
     "onsetIntervalMs": onsetIntervalMs, "presented": onsetMs != nil,
     "frameTimestampMs": nullValue(frameTimestampMs), "callbackTimestampMs": nullValue(callbackTimestampMs),
     "onsetMs": nullValue(onsetMs), "onsetLatenessMs": nullValue(onsetMs.map { $0 - Double(plannedOnsetMs) }),
     "outcome": outcome, "selectedInputSequence": nullValue(selectedInputSequence),
     "responseTimeMs": nullValue(responseTimeMs), "correctGoRtMs": nullValue(correctGoRtMs)]
  }
}
struct ReactionInput {
  let nativeTimestampMs: Double
  let dispatchTimestampMs: Double
  let target: String
  let pointerId: Int
  let nativeSequence: Int
  var inputKind = "direct_touch"
  var disposition = "anticipatory"
  var trialIndex: Int? = nil
  var anticipatoryForTrialIndex: Int? = nil
  var dispatchDelayMs: Double { dispatchTimestampMs - nativeTimestampMs }
  func dictionary() -> [String: Any] {
    ["nativeTimestampMs": nativeTimestampMs, "dispatchTimestampMs": dispatchTimestampMs,
     "dispatchDelayMs": dispatchDelayMs, "target": target, "pointerId": pointerId,
     "nativeSequence": nativeSequence, "inputKind": inputKind, "disposition": disposition,
     "trialIndex": nullValue(trialIndex), "anticipatoryForTrialIndex": nullValue(anticipatoryForTrialIndex)]
  }
}
struct ReactionScore {
  let trials: [ReactionTrial]
  let inputs: [ReactionInput]
  let counts: [String: Int]
  let features: [String: Any]?
}

enum ReactionCore {
  static func inputAdmission(retainedCount: Int, dispatchMs: Double, terminalCutoffMs: Double?) -> String {
    if let cutoff = terminalCutoffMs, dispatchMs >= cutoff { return "ignore_after_terminal" }
    if retainedCount >= ReactionConfig.inputLimit { return "overflow" }
    return "accept"
  }

  static func schedule(seed: UInt32) -> [ReactionTrial] {
    var state = seed
    func next() -> UInt32 { state = state &* 1664525 &+ 1013904223; return state }
    var practice = ["left", "left", "right", "right", "no_go", "no_go"]
    var scored = Array(repeating: "left", count: 24) + Array(repeating: "right", count: 24) + Array(repeating: "no_go", count: 12)
    for i in stride(from: practice.count - 1, through: 1, by: -1) { practice.swapAt(i, Int(next() % UInt32(i + 1))) }
    for i in stride(from: scored.count - 1, through: 1, by: -1) { scored.swapAt(i, Int(next() % UInt32(i + 1))) }
    let gaps = (0..<66).map { _ in 1500 + Int(next() % 401) }
    var onset = 2000
    return (practice + scored).enumerated().map { index, side in
      let trial = ReactionTrial(index: index, phase: index < 6 ? "practice" : "scored", stimulus: side, plannedOnsetMs: onset, onsetIntervalMs: gaps[index])
      onset += gaps[index]; return trial
    }
  }
  // Exact JCS for this fixed-key safe-integer ASCII schedule, not an arbitrary-JSON canonicalizer.
  static func scheduleCanonical(seed: UInt32, trials: [ReactionTrial]) -> String {
    let records = trials.map { t in
      "{\"index\":\(t.index),\"onset_interval_ms\":\(t.onsetIntervalMs),\"phase\":\"\(t.phase)\",\"planned_onset_ms\":\(t.plannedOnsetMs),\"stimulus\":\"\(t.stimulus)\"}"
    }.joined(separator: ",")
    return "{\"configuration_sha256\":\"\(ReactionConfig.sha256)\",\"schema_version\":\"1.0.0\",\"seed\":\(seed),\"trials\":[\(records)]}"
  }
  static func scheduleHash(seed: UInt32, trials: [ReactionTrial]) -> String {
    SHA256.hash(data: Data(scheduleCanonical(seed: seed, trials: trials).utf8)).map { String(format: "%02x", $0) }.joined()
  }
  static func quantile(_ sorted: [Double], _ p: Double) -> Double? {
    guard !sorted.isEmpty else { return nil }
    let index = Double(sorted.count - 1) * p; let lo = Int(floor(index)); let hi = min(lo + 1, sorted.count - 1)
    return sorted[lo] + (sorted[hi] - sorted[lo]) * (index - Double(lo))
  }
  static func rank(_ target: String) -> Int { target == "left" ? 0 : (target == "right" ? 1 : 2) }
  static func inputFault(_ input: ReactionInput) -> String? {
    if !input.nativeTimestampMs.isFinite || !input.dispatchTimestampMs.isFinite || input.dispatchDelayMs < 0 { return "NATIVE_CLOCK_INCONSISTENCY" }
    if input.inputKind != "direct_touch" { return "INPUT_MODE_UNSUPPORTED" }
    if input.dispatchDelayMs > ReactionConfig.budgetMs { return "INPUT_DISPATCH_DELAY_EXCEEDED" }
    return nil
  }
  static func frameFault(gap: Double, dispatch: Double, lateness: Double? = nil) -> String? {
    if !gap.isFinite || !dispatch.isFinite || gap < 0 || dispatch < 0 { return "NATIVE_CLOCK_INCONSISTENCY" }
    if gap > ReactionConfig.budgetMs { return "FRAME_GAP_EXCEEDED" }
    if dispatch > ReactionConfig.budgetMs { return "FRAME_CALLBACK_DELAY_EXCEEDED" }
    if let late = lateness {
      if !late.isFinite || late < 0 { return "NATIVE_CLOCK_INCONSISTENCY" }
      if late > ReactionConfig.budgetMs { return "SCHEDULED_ONSET_LATE" }
    }
    return nil
  }
  static func score(trials originalTrials: [ReactionTrial], inputs originalInputs: [ReactionInput], endedMs: Double, intact: Bool) -> ReactionScore {
    var trials = originalTrials
    var inputs = originalInputs.sorted { a, b in
      if a.nativeTimestampMs != b.nativeTimestampMs { return a.nativeTimestampMs < b.nativeTimestampMs }
      if rank(a.target) != rank(b.target) { return rank(a.target) < rank(b.target) }
      if a.pointerId != b.pointerId { return a.pointerId < b.pointerId }
      return a.nativeSequence < b.nativeSequence
    }
    let presentedIndices = trials.indices.filter { trials[$0].onsetMs != nil }
    var selected: [Int: ReactionInput] = [:]
    for i in trials.indices { trials[i].outcome = "unresolved"; trials[i].selectedInputSequence = nil; trials[i].responseTimeMs = nil; trials[i].correctGoRtMs = nil }
    for i in inputs.indices {
      inputs[i].trialIndex = nil; inputs[i].anticipatoryForTrialIndex = nil
      let time = inputs[i].nativeTimestampMs
      let within = presentedIndices.first { time >= trials[$0].onsetMs! && time < trials[$0].onsetMs! + ReactionConfig.windowMs }
      inputs[i].trialIndex = within.map { trials[$0].index }
      if inputFault(inputs[i]) != nil { inputs[i].disposition = inputs[i].inputKind == "direct_touch" ? "timing_fault" : "unsupported"; continue }
      if inputs[i].target == "outside" { inputs[i].disposition = "outside"; continue }
      if let trialIndex = within {
        if selected[trialIndex] != nil { inputs[i].disposition = "additional_response" }
        else { inputs[i].disposition = "selected"; selected[trialIndex] = inputs[i] }
      } else {
        let previous = presentedIndices.last { time >= trials[$0].onsetMs! + ReactionConfig.windowMs }
        let following = presentedIndices.first { time < trials[$0].onsetMs! }
        inputs[i].trialIndex = previous.map { trials[$0].index }; inputs[i].anticipatoryForTrialIndex = following.map { trials[$0].index }
        inputs[i].disposition = previous == nil ? "anticipatory" : "late"
      }
    }
    for i in presentedIndices {
      if let response = selected[i] {
        trials[i].selectedInputSequence = response.nativeSequence
        trials[i].responseTimeMs = response.nativeTimestampMs - trials[i].onsetMs!
        trials[i].outcome = trials[i].stimulus == "no_go" ? "commission" : (response.target == trials[i].stimulus ? "correct" : "wrong_choice")
        if trials[i].outcome == "correct" { trials[i].correctGoRtMs = trials[i].responseTimeMs }
      } else if endedMs >= trials[i].onsetMs! + ReactionConfig.windowMs { trials[i].outcome = trials[i].stimulus == "no_go" ? "correct_withhold" : "omission" }
    }
    let presented = presentedIndices.map { trials[$0] }; let scored = presented.filter { $0.phase == "scored" }
    let go = scored.filter { $0.stimulus != "no_go" }; let noGo = scored.filter { $0.stimulus == "no_go" }
    let correct = go.filter { $0.outcome == "correct" }.count; let omissions = go.filter { $0.outcome == "omission" }.count
    let wrong = go.filter { $0.outcome == "wrong_choice" }.count; let commissions = noGo.filter { $0.outcome == "commission" }.count
    let counts = ["presentedPractice": presented.filter { $0.phase == "practice" }.count, "presentedScored": scored.count,
                  "presentedGo": go.count, "presentedNoGo": noGo.count, "completedScored": scored.filter { endedMs >= $0.onsetMs! + ReactionConfig.windowMs }.count,
                  "correctGo": correct, "omissions": omissions, "wrongGo": wrong, "noGoErrors": commissions,
                  "correctWithholds": noGo.filter { $0.outcome == "correct_withhold" }.count]
    let times = go.compactMap { $0.correctGoRtMs }.sorted()
    var features: [String: Any]? = nil
    if intact {
      let q25 = quantile(times, 0.25); let q75 = quantile(times, 0.75)
      let iqr: Double? = (q25 != nil && q75 != nil) ? q75! - q25! : nil
      features = ["medianRtMs": nullValue(quantile(times, 0.5)), "iqrRtMs": nullValue(iqr), "p90RtMs": nullValue(quantile(times, 0.9)),
                  "omissionRate": go.isEmpty ? 0.0 : Double(omissions) / Double(go.count),
                  "wrongGoRate": go.isEmpty ? 0.0 : Double(wrong) / Double(go.count),
                  "noGoErrorRate": noGo.isEmpty ? 0.0 : Double(commissions) / Double(noGo.count)]
    }
    return ReactionScore(trials: trials, inputs: inputs, counts: counts, features: features)
  }
}
