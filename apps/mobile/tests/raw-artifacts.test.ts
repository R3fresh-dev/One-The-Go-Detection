import test from "node:test";
import assert from "node:assert/strict";
import {
  decodeRawRecording,
  verifyRawPermission,
} from "../src/core/rawArtifacts";
import { digestBytes, clone, utf8 } from "../src/core/integrity";
import fixture from "../testfixtures/backend-raw-recordings.json";
import { parseRawRecordingStatus } from "../src/core/rawRecordings";
import { NamespaceGate } from "../src/core/namespaceGate";
import { deferred } from "./support/customer";
import readerFixture from "../testfixtures/signed-reader-raw-ecg.json";
import { canonicalJson, digest } from "../src/core/integrity";
import { createPublicKey, verify } from "node:crypto";
function rawFrame() {
  const magic = utf8("OTGD-EYE-ROI-v1\n"),
    bytes = new Uint8Array(magic.length + 8 + 2 * (12 + 4));
  bytes.set(magic);
  const view = new DataView(bytes.buffer);
  view.setUint16(magic.length, 2, true);
  view.setUint16(magic.length + 2, 2, true);
  view.setUint32(magic.length + 4, 2, true);
  for (let index = 0; index < 2; index++) {
    const at = magic.length + 8 + index * 16;
    view.setFloat64(at, 100 + index * 16, true);
    view.setUint32(at + 8, index, true);
    bytes.set([30, 10, 10, 30], at + 12);
  }
  return bytes;
}
const dto = (bytes: Uint8Array) => ({
  format: "OTGD-EYE-ROI-v1",
  media_type: "application/octet-stream",
  sha256: digestBytes(bytes),
  size_bytes: bytes.length,
  chunks: [Buffer.from(bytes).toString("base64")],
});

test("native ROI bytes validate exact codec, frame geometry, sequence, timing, digest and bounded memory handoff", () => {
  const bytes = rawFrame(),
    decoded = decodeRawRecording(dto(bytes), "eye_video");
  assert.deepEqual(decoded.bytes, bytes);
  assert.equal(decoded.media_type, "application/octet-stream");
  for (const mutate of [
    (value: any) => value.chunks.push("AA=="),
    (value: any) => value.size_bytes++,
    (value: any) => (value.sha256 = "1".repeat(64)),
    (value: any) => (value.format = "MP4"),
    (value: any) => (value.media_type = "video/mp4"),
    (value: any) => (value.chunks[0] = "!notbase64!"),
    (value: any) => (value.uri = "/private/plaintext-video.mp4"),
  ]) {
    const changed: any = dto(bytes);
    mutate(changed);
    assert.throws(() => decodeRawRecording(changed, "eye_video"));
  }
  assert.throws(() => decodeRawRecording(dto(bytes), "ecg_waveform"));
  for (const mutate of [
    (v: DataView) => v.setUint16(16, 129, true),
    (v: DataView) => v.setUint32(20, 301, true),
    (v: DataView) => v.setUint32(32, 2, true),
    (v: DataView) => v.setFloat64(40, 90, true),
  ]) {
    const altered = bytes.slice();
    mutate(new DataView(altered.buffer));
    assert.throws(() => decodeRawRecording(dto(altered), "eye_video"));
  }
});

test("fresh acquisition authority must match exact current optional receipt and cannot bypass offline or cross-device stop", (context) => {
  context.mock.timers.enable({
    apis: ["Date"],
    now: Date.parse("2026-10-11T12:00:00Z"),
  });
  const status = parseRawRecordingStatus(fixture, fixture.study_id),
    policy = status.policy!;
  const permission = {
    record: true,
    upload: true,
    receipt_id: status.receipt_id!,
    policy_id: policy.policy_id,
    policy_version: policy.version,
    policy_sha256: policy.sha256,
    raw_notice_version: policy.raw_notice.version,
    raw_notice_sha256: policy.raw_notice.sha256,
  };
  assert.deepEqual(
    verifyRawPermission(permission, status, "eye_video", []),
    permission,
  );
  assert.throws(
    () => verifyRawPermission(permission, status, "eye_video", ["eye_video"]),
    /fresh capture start/,
  );
  for (const key of [
    "record",
    "upload",
    "receipt_id",
    "policy_id",
    "policy_version",
    "policy_sha256",
    "raw_notice_version",
    "raw_notice_sha256",
  ]) {
    const changed: any = clone(permission);
    changed[key] =
      typeof changed[key] === "boolean" ? !changed[key] : "changed";
    assert.throws(() => verifyRawPermission(changed, status, "eye_video", []));
  }
  const revoked = clone(status);
  revoked.choices.eye_video = { record: false, upload: false };
  assert.throws(() =>
    verifyRawPermission(permission, revoked, "eye_video", []),
  );
  context.mock.timers.setTime(Date.parse("2026-11-01T00:00:00Z"));
  assert.throws(() => verifyRawPermission(permission, status, "eye_video", []));
});

test("actual reader encoder handoff preserves fictional device-signed ECG chunks, acquisition anchors and canonical bytes", () => {
  const raw = decodeRawRecording(readerFixture.recording, "ecg_waveform");
  assert.equal(raw.sha256, readerFixture.recording.sha256);
  assert.deepEqual(
    raw.evidence!.sample_chunks,
    readerFixture.capture.sampleChunks,
  );
  const key = createPublicKey(readerFixture.device_public_key_pem);
  for (const proof of [
    readerFixture.capture,
    ...readerFixture.capture.sampleChunks,
  ])
    assert.equal(
      verify(
        "sha256",
        Buffer.from("OTGD-CAPTURE-v1\n" + canonicalJson(proof.envelope)),
        key,
        Buffer.from(proof.signature, "base64"),
      ),
      true,
      "Only a fictional test peripheral key is used; this is not hardware qualification.",
    );
  const change = (mutate: (body: any) => void) => {
    const body = clone(raw.evidence);
    mutate(body);
    const bytes = utf8("OTGD-ECG-SAMPLES-v1\n" + canonicalJson(body));
    return {
      ...clone(readerFixture.recording),
      size_bytes: bytes.length,
      sha256: digestBytes(bytes),
      chunks: [Buffer.from(bytes).toString("base64")],
    };
  };
  for (const mutate of [
    (b: any) => b.sample_chunks[0].normalized_payload.samples[0].value++,
    (b: any) =>
      (b.sample_chunks[0].envelope.owner_ref =
        "00000000-0000-4000-8000-000000000001"),
    (b: any) => (b.sample_chunks[0].envelope.sequence = b.envelope.sequence),
    (b: any) =>
      (b.sample_chunks[0].normalized_payload.acquisition_ended_monotonic_us = 1),
    (b: any) =>
      (b.sample_chunks = Array.from({ length: 65 }, () => b.sample_chunks[0])),
    (b: any) => (b.normalized_payload.modality = "ppg"),
  ])
    assert.throws(() => decodeRawRecording(change(mutate), "ecg_waveform"));
  raw.bytes.fill(0);
});

test("two concurrent opens share serialized key initialization while independent namespaces and later recovery remain available", async () => {
  const gate = new NamespaceGate(),
    entered = deferred<void>(),
    release = deferred<void>(),
    events: string[] = [];
  const first = gate.run("account-A", async () => {
    events.push("first-open");
    entered.resolve();
    await release.promise;
    events.push("first-ready");
    return "handle1";
  });
  await entered.promise;
  const second = gate.run("account-A", async () => {
    events.push("second-open");
    return "handle2";
  });
  const other = await gate.run("account-B", async () => {
    events.push("other-account");
    return "handleB";
  });
  assert.equal(other, "handleB");
  assert.deepEqual(events, ["first-open", "other-account"]);
  release.resolve();
  assert.deepEqual(await Promise.all([first, second]), ["handle1", "handle2"]);
  assert.deepEqual(events, [
    "first-open",
    "other-account",
    "first-ready",
    "second-open",
  ]);
  await assert.rejects(
    gate.run("account-A", async () => {
      throw Error("key failure");
    }),
  );
  assert.equal(await gate.run("account-A", async () => 42), 42);
});
