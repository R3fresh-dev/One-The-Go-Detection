package expo.modules.otgdreaction

import org.json.JSONObject
import org.junit.Assert.*
import org.junit.Test

class ReactionCoreTest {
  private fun fixture(): JSONObject = JSONObject(requireNotNull(javaClass.classLoader?.getResource("golden.json")).readText())
  private fun number(expected: JSONObject, key: String, actual: Double?) {
    if (expected.isNull(key)) assertNull(key, actual) else assertEquals(key, expected.getDouble(key), requireNotNull(actual), 1e-6)
  }
  @Test fun frozenLiteralSchedulesAndHashes() {
    val f = fixture(); assertEquals(ReactionConfig.SHA256, f.getString("configuration_sha256"))
    val schedules = f.getJSONArray("schedules")
    for (i in 0 until schedules.length()) {
      val expected = schedules.getJSONObject(i); val source = expected.getJSONObject("schedule"); val seed = source.getLong("seed")
      val actual = ReactionCore.schedule(seed); val expectedTrials = source.getJSONArray("trials")
      assertEquals(66, actual.size); assertEquals(66, expectedTrials.length())
      for (j in actual.indices) {
        val e = expectedTrials.getJSONObject(j); val a = actual[j]
        assertEquals(e.getInt("index"), a.index); assertEquals(e.getString("phase"), a.phase); assertEquals(e.getString("stimulus"), a.stimulus)
        assertEquals(e.getInt("planned_onset_ms"), a.plannedOnsetMs); assertEquals(e.getInt("onset_interval_ms"), a.onsetIntervalMs)
      }
      assertEquals(expected.getString("schedule_sha256"), ReactionCore.scheduleHash(seed, actual))
      assertEquals(expected.getDouble("expected_no_lateness_terminal_cutoff_ms"), actual.last().plannedOnsetMs + ReactionConfig.WINDOW_MS + ReactionConfig.DRAIN_MS, 1e-6)
    }
  }
  @Test fun allLiteralTrialBoundaryVectors() {
    val vectors = fixture().getJSONArray("trial_scoring_vectors")
    for (i in 0 until vectors.length()) {
      val v = vectors.getJSONObject(i); val expected = v.getJSONObject("expected"); val onset = v.getDouble("onset_ms")
      val t = Trial(0,"scored",v.getString("stimulus"),onset.toInt(),1700, onsetMs=onset)
      val sourceInputs = v.getJSONArray("inputs"); val cutoff = if (v.has("terminal_cutoff_ms")) v.getDouble("terminal_cutoff_ms") else null
      val inputs = mutableListOf<TaskInput>(); var ignored = 0; var fault: String? = null
      for (j in 0 until sourceInputs.length()) {
        val e = sourceInputs.getJSONObject(j)
        if (ReactionCore.inputAdmission(inputs.size,e.getDouble("dispatch_timestamp_ms"),cutoff) == "ignore_after_terminal") { ignored++; continue }
        val input = TaskInput(e.getDouble("native_timestamp_ms"),e.getDouble("dispatch_timestamp_ms"),e.getString("target"),e.getInt("pointer_id"),e.getInt("native_sequence"),e.getString("input_kind"))
        inputs.add(input); fault = fault ?: ReactionCore.inputFault(input)
      }
      val result = ReactionCore.score(listOf(t),inputs,cutoff ?: onset+1100, fault == null)
      if (expected.getString("run_integrity") == "invalid") {
        assertEquals(expected.getJSONArray("quality_flags").getString(0),fault); assertNull(result.features)
      } else {
        assertNull(v.getString("case_id"),fault)
        assertEquals(v.getString("case_id"),expected.getString("trial_outcome"),result.trials[0].outcome)
        if (expected.isNull("selected_input_sequence")) assertNull(t.selectedInputSequence) else assertEquals(expected.getInt("selected_input_sequence"), t.selectedInputSequence)
        number(expected,"response_time_ms",t.responseTimeMs); number(expected,"correct_go_rt_ms",t.correctGoRtMs)
        if (expected.has("input_dispositions")) assertEquals(expected.getJSONArray("input_dispositions").toList(),result.inputs.map { it.disposition })
        if (expected.has("sorted_native_sequences")) assertEquals(expected.getJSONArray("sorted_native_sequences").toList(),result.inputs.map { it.nativeSequence })
        if (expected.has("ignored_after_terminal_count")) assertEquals(expected.getInt("ignored_after_terminal_count"),ignored)
      }
    }
  }
  @Test fun aggregatesPracticeExclusionAndNullableNoResponseFeatures() {
    val trials = ReactionCore.schedule(1).onEach { it.onsetMs=it.plannedOnsetMs.toDouble() }
    val inputs = trials.filter { it.stimulus != "no_go" }.mapIndexed { index,t -> TaskInput(t.onsetMs!!+300,t.onsetMs!!+305,t.stimulus,0,index) }
    val result = ReactionCore.score(trials,inputs,trials.last().onsetMs!!+1100,true)
    assertEquals(6,result.counts["presentedPractice"]); assertEquals(60,result.counts["presentedScored"])
    assertEquals(48,result.counts["correctGo"]); assertEquals(12,result.counts["correctWithholds"])
    assertEquals(300.0,result.features!!["medianRtMs"]); assertEquals(0.0,result.features["iqrRtMs"]); assertEquals(300.0,result.features["p90RtMs"])
    val omitted = ReactionCore.score(trials,emptyList(),trials.last().onsetMs!!+1100,true)
    assertEquals(48,omitted.counts["omissions"]); assertEquals(1.0,omitted.features!!["omissionRate"])
    assertNull(omitted.features["medianRtMs"]); assertNull(omitted.features["iqrRtMs"]); assertNull(omitted.features["p90RtMs"])
    val partial = ReactionCore.score(trials.take(16),inputs,28000.0,false)
    assertNull(partial.features); assertEquals(10,partial.counts["presentedScored"])
  }
  @Test fun quantilesAndDevelopmentBudgets() {
    val expected = fixture().getJSONArray("aggregate_vectors").getJSONObject(0).getJSONObject("expected")
    val times = listOf(200.0,250.0,300.0,350.0,400.0)
    number(expected,"q25_ms",ReactionCore.quantile(times,.25)); number(expected,"median_rt_ms",ReactionCore.quantile(times,.5))
    number(expected,"q75_ms",ReactionCore.quantile(times,.75)); number(expected,"p90_rt_ms",ReactionCore.quantile(times,.9))
    assertNull(ReactionCore.frameFault(100.0,100.0,100.0))
    assertEquals("FRAME_GAP_EXCEEDED",ReactionCore.frameFault(100.001,0.0))
    assertEquals("FRAME_CALLBACK_DELAY_EXCEEDED",ReactionCore.frameFault(0.0,100.001))
    assertEquals("SCHEDULED_ONSET_LATE",ReactionCore.frameFault(0.0,0.0,100.001))
    assertEquals("NATIVE_CLOCK_INCONSISTENCY",ReactionCore.frameFault(-1.0,0.0))
  }
  @Test fun terminalDrainOverflowAndPendingCancellation() {
    assertEquals("accept",ReactionCore.inputAdmission(1023,11099.999,11100.0))
    assertEquals("ignore_after_terminal",ReactionCore.inputAdmission(1024,11100.0,11100.0))
    assertEquals("overflow",ReactionCore.inputAdmission(1024,11099.0,11100.0))
    val canceled = ReactionTerminalLatch(); canceled.requestCancel("USER_CANCELED")
    assertEquals(false,canceled.commit(true)); assertNull(canceled.commit(true)); assertEquals("USER_CANCELED",canceled.cancellation)
    val completed = ReactionTerminalLatch(); assertEquals(true,completed.commit(true)); completed.requestCancel("ROUTE_HIDDEN"); assertNull(completed.commit(false)); assertNull(completed.cancellation)
  }
  @Test fun worstCaseBoundedEvidenceRemainsUnderCompanionLimit() {
    val trials = ReactionCore.schedule(4294967295).onEach { it.onsetMs=it.plannedOnsetMs.toDouble(); it.frameTimestampMs=it.onsetMs; it.callbackTimestampMs=it.onsetMs!!+16.666666666 }
    val inputs = List(1024) { i -> TaskInput(12345.123456789+i,12350.123456789+i,"outside",i,i) }
    val evidence = ReactionCore.score(trials,inputs,115000.0,false)
    val bytes = JSONObject(mapOf("trials" to evidence.trials.map { it.map() },"inputs" to evidence.inputs.map { it.map() })).toString().toByteArray(Charsets.UTF_8).size
    assertTrue("Native arrays plus 16KiB of bounded metadata must fit 512KiB",bytes+16384 < 512*1024)
  }
}
