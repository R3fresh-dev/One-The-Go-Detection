import Foundation
import XCTest
@testable import OTGDReactionCore

final class ReactionCoreTests: XCTestCase {
  private func fixture() throws -> [String: Any] {
    let url = URL(fileURLWithPath: #filePath).deletingLastPathComponent().deletingLastPathComponent().deletingLastPathComponent().appendingPathComponent("fixtures/golden.json")
    return try XCTUnwrap(JSONSerialization.jsonObject(with: Data(contentsOf: url)) as? [String: Any])
  }
  private func number(_ expected: [String: Any], _ key: String, _ actual: Double?) {
    if expected[key] is NSNull { XCTAssertNil(actual, key) }
    else { XCTAssertNotNil(actual, key); XCTAssertEqual((expected[key] as! NSNumber).doubleValue, actual ?? .nan, accuracy: 1e-6, key) }
  }
  func testFrozenLiteralSchedulesAndHashes() throws {
    let f = try fixture(); XCTAssertEqual(f["configuration_sha256"] as? String, ReactionConfig.sha256)
    for expected in f["schedules"] as! [[String: Any]] {
      let source = expected["schedule"] as! [String: Any], seed = (source["seed"] as! NSNumber).uint32Value
      let actual = ReactionCore.schedule(seed: seed), literal = source["trials"] as! [[String: Any]]
      XCTAssertEqual(actual.count, 66); XCTAssertEqual(literal.count, 66)
      for (index, a) in actual.enumerated() {
        let e = literal[index]; XCTAssertEqual(a.index, e["index"] as! Int); XCTAssertEqual(a.phase, e["phase"] as! String)
        XCTAssertEqual(a.stimulus, e["stimulus"] as! String); XCTAssertEqual(a.plannedOnsetMs, e["planned_onset_ms"] as! Int); XCTAssertEqual(a.onsetIntervalMs, e["onset_interval_ms"] as! Int)
      }
      XCTAssertEqual(ReactionCore.scheduleHash(seed: seed, trials: actual), expected["schedule_sha256"] as! String)
      XCTAssertEqual(Double(actual.last!.plannedOnsetMs)+ReactionConfig.windowMs+ReactionConfig.drainMs, (expected["expected_no_lateness_terminal_cutoff_ms"] as! NSNumber).doubleValue)
    }
  }
  func testAllLiteralTrialBoundaryVectors() throws {
    for v in try fixture()["trial_scoring_vectors"] as! [[String: Any]] {
      let expected = v["expected"] as! [String: Any], onset = (v["onset_ms"] as! NSNumber).doubleValue
      let trial = ReactionTrial(index: 0, phase: "scored", stimulus: v["stimulus"] as! String, plannedOnsetMs: Int(onset), onsetIntervalMs: 1700, onsetMs: onset)
      let cutoff = (v["terminal_cutoff_ms"] as? NSNumber)?.doubleValue
      var inputs: [ReactionInput] = []; var ignored = 0; var fault: String? = nil
      for item in v["inputs"] as! [[String: Any]] {
        let dispatch = (item["dispatch_timestamp_ms"] as! NSNumber).doubleValue
        if ReactionCore.inputAdmission(retainedCount: inputs.count, dispatchMs: dispatch, terminalCutoffMs: cutoff) == "ignore_after_terminal" { ignored += 1; continue }
        let input = ReactionInput(nativeTimestampMs: (item["native_timestamp_ms"] as! NSNumber).doubleValue, dispatchTimestampMs: dispatch, target: item["target"] as! String, pointerId: item["pointer_id"] as! Int, nativeSequence: item["native_sequence"] as! Int, inputKind: item["input_kind"] as! String)
        inputs.append(input); fault = fault ?? ReactionCore.inputFault(input)
      }
      let result = ReactionCore.score(trials: [trial], inputs: inputs, endedMs: cutoff ?? onset+1100, intact: fault == nil)
      if expected["run_integrity"] as! String == "invalid" { XCTAssertEqual(fault, (expected["quality_flags"] as! [String])[0]); XCTAssertNil(result.features) }
      else {
        XCTAssertNil(fault, v["case_id"] as! String); let t = result.trials[0]
        XCTAssertEqual(t.outcome, expected["trial_outcome"] as! String, v["case_id"] as! String)
        XCTAssertEqual(t.selectedInputSequence, expected["selected_input_sequence"] as? Int)
        number(expected,"response_time_ms",t.responseTimeMs); number(expected,"correct_go_rt_ms",t.correctGoRtMs)
        if let dispositions = expected["input_dispositions"] as? [String] { XCTAssertEqual(result.inputs.map { $0.disposition },dispositions) }
        if let sequences = expected["sorted_native_sequences"] as? [Int] { XCTAssertEqual(result.inputs.map { $0.nativeSequence },sequences) }
        if let count = expected["ignored_after_terminal_count"] as? Int { XCTAssertEqual(ignored,count) }
      }
    }
  }
  func testAggregatesAndPracticeExclusion() {
    var trials = ReactionCore.schedule(seed: 1)
    for i in trials.indices { trials[i].onsetMs = Double(trials[i].plannedOnsetMs) }
    let inputs = trials.filter { $0.stimulus != "no_go" }.enumerated().map { index,t in ReactionInput(nativeTimestampMs: t.onsetMs!+300, dispatchTimestampMs: t.onsetMs!+305, target: t.stimulus, pointerId: 0, nativeSequence: index) }
    let result = ReactionCore.score(trials: trials, inputs: inputs, endedMs: trials.last!.onsetMs!+1100, intact: true)
    XCTAssertEqual(result.counts["presentedPractice"],6); XCTAssertEqual(result.counts["presentedScored"],60); XCTAssertEqual(result.counts["correctGo"],48); XCTAssertEqual(result.counts["correctWithholds"],12)
    XCTAssertEqual(result.features?["medianRtMs"] as? Double,300); XCTAssertEqual(result.features?["iqrRtMs"] as? Double,0); XCTAssertEqual(result.features?["p90RtMs"] as? Double,300)
    let omitted = ReactionCore.score(trials: trials, inputs: [], endedMs: trials.last!.onsetMs!+1100, intact: true)
    XCTAssertEqual(omitted.counts["omissions"],48); XCTAssertEqual(omitted.features?["omissionRate"] as? Double,1)
    XCTAssertTrue(omitted.features?["medianRtMs"] is NSNull); XCTAssertTrue(omitted.features?["iqrRtMs"] is NSNull); XCTAssertTrue(omitted.features?["p90RtMs"] is NSNull)
    let partial = ReactionCore.score(trials: Array(trials.prefix(16)), inputs: inputs, endedMs: 28000, intact: false)
    XCTAssertNil(partial.features); XCTAssertEqual(partial.counts["presentedScored"],10)
  }
  func testQuantileBudgetsDrainAndTerminalOnce() throws {
    let expected = (try fixture()["aggregate_vectors"] as! [[String: Any]])[0]["expected"] as! [String: Any]
    let values = [200.0,250,300,350,400]
    number(expected,"q25_ms",ReactionCore.quantile(values,0.25)); number(expected,"median_rt_ms",ReactionCore.quantile(values,0.5)); number(expected,"q75_ms",ReactionCore.quantile(values,0.75)); number(expected,"p90_rt_ms",ReactionCore.quantile(values,0.9))
    XCTAssertNil(ReactionCore.frameFault(gap: 100,dispatch: 100,lateness: 100))
    XCTAssertEqual(ReactionCore.frameFault(gap: 100.001,dispatch: 0),"FRAME_GAP_EXCEEDED")
    XCTAssertEqual(ReactionCore.frameFault(gap: 0,dispatch: 100.001),"FRAME_CALLBACK_DELAY_EXCEEDED")
    XCTAssertEqual(ReactionCore.frameFault(gap: 0,dispatch: 0,lateness: 100.001),"SCHEDULED_ONSET_LATE")
    XCTAssertEqual(ReactionCore.inputAdmission(retainedCount: 1023,dispatchMs: 11099.999,terminalCutoffMs: 11100),"accept")
    XCTAssertEqual(ReactionCore.inputAdmission(retainedCount: 1024,dispatchMs: 11100,terminalCutoffMs: 11100),"ignore_after_terminal")
    XCTAssertEqual(ReactionCore.inputAdmission(retainedCount: 1024,dispatchMs: 11099,terminalCutoffMs: 11100),"overflow")
    let canceled = ReactionTerminalLatch(); canceled.requestCancel("USER_CANCELED"); XCTAssertEqual(canceled.commit(true),false); XCTAssertNil(canceled.commit(true))
    let completed = ReactionTerminalLatch(); XCTAssertEqual(completed.commit(true),true); completed.requestCancel("ROUTE_HIDDEN"); XCTAssertNil(completed.commit(false)); XCTAssertNil(completed.cancellation)
  }
  func testWorstCaseEvidenceBound() throws {
    var trials = ReactionCore.schedule(seed: UInt32.max)
    for i in trials.indices { trials[i].onsetMs = Double(trials[i].plannedOnsetMs); trials[i].frameTimestampMs = trials[i].onsetMs; trials[i].callbackTimestampMs = trials[i].onsetMs!+16.66666666 }
    let inputs = (0..<1024).map { i in ReactionInput(nativeTimestampMs: 12345.123456789+Double(i),dispatchTimestampMs: 12350.123456789+Double(i),target: "outside",pointerId: i,nativeSequence: i) }
    let evidence = ReactionCore.score(trials: trials,inputs: inputs,endedMs: 115000,intact: false)
    let data = try JSONSerialization.data(withJSONObject: ["trials":evidence.trials.map { $0.dictionary() },"inputs":evidence.inputs.map { $0.dictionary() }])
    XCTAssertLessThan(data.count+16384,512*1024)
  }
}
