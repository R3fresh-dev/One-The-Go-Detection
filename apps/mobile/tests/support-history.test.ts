import test from "node:test";
import assert from "node:assert/strict";
import { createDiagnostics } from "../src/core/diagnostics";
import {
  HistoryViewMemory,
  pendingSync,
  sortHistoryRows,
} from "../src/core/historyView";

test("support diagnostics copy only bounded explicit fields, never an error payload", () => {
  const contaminated = {
    appVersion: "0.2.0",
    buildNumber: "42",
    platform: "ios",
    platformVersion: "26.4",
    environment: "qa",
    publicServiceOrigin:
      "https://qa.service.invalid/path?token=secret#callback",
    capabilityCodes: [
      "NO_QUALIFIED_CONFIGURATION",
      "secret-account-email@example.invalid",
    ],
    syncState: "retry_wait",
    errorCode: "NETWORK_ERROR",
    supportRequestId: "9e2e3d56-9a8a-4e51-bbcc-227d73c93130",
    token: "bearer-secret",
    profile: { weight_kg: 73 },
    message: "saliva 500; user@example.invalid",
  };
  const text = createDiagnostics(contaminated),
    report = JSON.parse(text);
  assert.equal(report.public_service_origin, "https://qa.service.invalid");
  assert.equal(report.last_error_category, "network_unavailable");
  assert.equal(report.support_request_id, contaminated.supportRequestId);
  assert.deepEqual(report.capability_codes, [
    "NO_QUALIFIED_CONFIGURATION",
    "OTHER_CAPABILITY_CODE",
  ]);
  for (const forbidden of [
    "secret",
    "saliva",
    "weight_kg",
    "@",
    "callback",
    "message",
    "profile",
  ])
    assert.ok(!text.includes(forbidden));
});
test("untrusted diagnostics strings cannot become fields or copied references", () => {
  const text = createDiagnostics({
    appVersion: "0.2.0\nsecret",
    buildNumber: {},
    platform: "email@example.invalid",
    platformVersion: "id-secret",
    environment: "token-secret",
    publicServiceOrigin: "https://user:password@host.invalid/path",
    errorCode: "secret error body",
    supportRequestId: "access-token",
    syncState: "private-record",
    capabilityCodes: ["secret".repeat(50_000)],
  });
  const report = JSON.parse(text);
  assert.equal(report.public_service_origin, "unavailable");
  assert.equal(report.support_request_id, null);
  assert.equal(report.last_error_category, "other_error");
  assert.ok(!/secret|password|private-record|access-token/.test(text));
  assert.ok(text.length < 1024);
});
test("history detail round-trip keeps filters, selected IDs and scroll only in the current workspace epoch", () => {
  const memory = new HistoryViewMemory(),
    owner = {};
  memory.update(owner, "guest-1", {
    filter: "pending",
    search: "abc",
    selected: ["one"],
    selectionMode: true,
    scrollY: 1042,
  });
  assert.deepEqual(memory.read(owner, "guest-1"), {
    filter: "pending",
    search: "abc",
    from: "",
    to: "",
    selected: ["one"],
    selectionMode: true,
    scrollY: 1042,
  });
  const copy = memory.read(owner, "guest-1");
  copy.selected.push("foreign");
  assert.deepEqual(memory.read(owner, "guest-1").selected, ["one"]);
  assert.equal(memory.read(owner, "account-1").filter, "all");
  assert.equal(memory.read(owner, "account-1").scrollY, 0);
  assert.deepEqual(memory.read({}, "account-1").selected, []);
});
test("pending sync means explicitly requested delivery, not local saves or retired records", () => {
  for (const state of [
    "queued",
    "retry_wait",
    "blocked",
    "awaiting_result",
    "conflict",
  ])
    assert.equal(pendingSync(state), true);
  for (const state of [
    "local_draft",
    "local_finalized",
    "synced",
    "quarantined",
    "unknown",
  ])
    assert.equal(pendingSync(state), false);
});

test("mixed local and synced history uses acquisition time and stable identity ties", () => {
  const rows = [
    { id: "local-old", createdAt: "2026-10-09T23:00:00Z" },
    { id: "remote-new", createdAt: "2026-10-10T18:00:00.001Z" },
    { id: "local-a", createdAt: "2026-10-10T18:00:00Z" },
    { id: "remote-z", createdAt: "2026-10-10T18:00:00.000Z" },
  ];
  assert.deepEqual(
    sortHistoryRows(rows).map((row) => row.id),
    ["remote-new", "remote-z", "local-a", "local-old"],
  );
  assert.equal(rows[0]!.id, "local-old");
});
