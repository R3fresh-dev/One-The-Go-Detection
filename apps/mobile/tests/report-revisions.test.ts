import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { randomUUID } from "node:crypto";
import { URL } from "node:url";
import { emptyWorkspace } from "../src/core/domain";
import { parseRemoteCheck } from "../src/core/remote";
import {
  beginReportRefresh,
  parseReportDetail,
  parseReportList,
  reportArchiveRecords,
  verifyReportArchiveIndex,
  verifyReportCache,
  verifyReportChain,
  type ReportCompanion,
} from "../src/core/reportRevisions";
import { canonicalJson, clone, digest, utf8 } from "../src/core/integrity";
import type { Capabilities } from "../src/core/types";

const wire = JSON.parse(
  readFileSync(
    new URL(
      "../../../services/api/tests/fixtures/report-revision-wire.json",
      import.meta.url,
    ),
    "utf8",
  ),
);
function fixture() {
  const state = emptyWorkspace(
    "fictional-report-contract",
    wire.base.created_at,
    wire.data_generation,
  );
  state.capabilities = { account_ref: wire.account_ref } as Capabilities;
  const check = parseRemoteCheck(clone(wire.base), state);
  return { state, check };
}
function rehash(item: ReportCompanion): ReportCompanion {
  item.revision_sha256 = digest(item.descriptor);
  item.result.revision_sha256 = item.revision_sha256;
  item.result_sha256 = digest(item.result);
  return item;
}
test("actual backend correction and delayed reanalysis preserve immutable original evidence and exact carried-forward readings", () => {
  const { check } = fixture(),
    original = digest(check),
    list = parseReportList(wire.list, check),
    companions: ReportCompanion[] = [];
  for (const detail of wire.details)
    companions.push(parseReportDetail(detail, check, list, companions));
  assert.equal(companions.length, 2);
  assert.equal(companions[0]!.descriptor.report.kind, "correction");
  assert.equal(companions[1]!.descriptor.report.kind, "reanalysis");
  assert.equal(
    companions[1]!.result.replaces_result_id,
    companions[0]!.result.result_id,
  );
  assert.equal(
    companions[0]!.result.replaces_result_id,
    check.result!.result_id,
  );
  assert.equal(digest(check), original);
  assert.ok(
    companions.every(
      (item) =>
        item.result.target_at === check.snapshot.target_at &&
        item.result.inference_available === false &&
        item.result.probability === null,
    ),
  );
});
test("report list rejects another generation, changed original time, duplicate IDs, gaps and mutable result identity", () => {
  const { check } = fixture();
  for (const mutate of [
    (v: any) => {
      v.data_generation++;
    },
    (v: any) => {
      v.original_target_at = "2040-01-01T00:00:00Z";
    },
    (v: any) => {
      v.items[1].revision_id = v.items[0].revision_id;
    },
    (v: any) => {
      v.items[1].sequence = 3;
    },
    (v: any) => {
      v.base_result_id = randomUUID();
    },
    (v: any) => {
      v.items[0].next_revision_id = null;
    },
  ]) {
    const value = clone(wire.list);
    mutate(value);
    assert.throws(() => parseReportList(value, check));
  }
});
test("unknown companion fields/versions and inference output fail even after descriptor and result hashes are recomputed", () => {
  const { check } = fixture();
  for (const mutate of [
    (v: any) => {
      v.schema_version = "2.0.0";
    },
    (v: any) => {
      v.descriptor.report.diagnosis = "extra";
    },
    (v: any) => {
      v.result.probability = 0.5;
    },
    (v: any) => {
      v.result.model_id = "not-supported";
    },
    (v: any) => {
      v.result.result_kind = "original_result";
    },
    (v: any) => {
      v.result.evaluated_at = "2040-01-01T00:00:00Z";
    },
    (v: any) => {
      v.accepted_at = "2026-02-30T33:00:00Z";
      v.result.evaluated_at = v.accepted_at;
    },
  ]) {
    const value = clone(wire.companions[0]);
    mutate(value);
    rehash(value);
    assert.throws(() => verifyReportChain([value], check));
  }
});
test("rehashed report changes cannot move specimen collection, reuse prior analytical identities or misstate original units", () => {
  const { check } = fixture();
  for (const mutate of [
    (v: ReportCompanion) => {
      v.descriptor.original_collected_at = "2040-01-01T00:00:00Z";
    },
    (v: ReportCompanion) => {
      v.descriptor.report.replacement_measurements[0]!.measurement_id =
        check.snapshot.saliva[0]!.measurement_id!;
    },
    (v: ReportCompanion) => {
      v.descriptor.report.replacement_measurements[0]!.sample_id = randomUUID();
    },
    (v: ReportCompanion) => {
      (
        v.descriptor.report.replacement_measurements[0]!.original_report as any
      ).value = 99_999_999;
    },
    (v: ReportCompanion) => {
      v.descriptor.report.authorization.operator_account_ref = randomUUID();
    },
    (v: ReportCompanion) => {
      v.descriptor.report.source_report.version_id = "null";
    },
  ]) {
    const value = clone(wire.companions[0]) as ReportCompanion;
    mutate(value);
    rehash(value);
    assert.throws(() => verifyReportChain([value], check));
  }
});
test("rehashed revised results cannot promote an originally invalid check or relabel evaluation as a new assessment", () => {
  const { check } = fixture();
  check.result!.state = "invalid";
  const value = clone(wire.companions[0]) as ReportCompanion;
  assert.throws(
    () => verifyReportChain([value], check),
    /invalidity|analytical evidence/,
  );
  value.result.state = "invalid";
  rehash(value);
  assert.equal(verifyReportChain([value], check)[0]!.result.state, "invalid");
  value.result.target_at = value.result.evaluated_at;
  rehash(value);
  assert.throws(() => verifyReportChain([value], check), /timing/);
});
test("known incomplete report cache blocks device exports and append-only cache cannot regress", () => {
  const { check } = fixture(),
    list = parseReportList(wire.list, check);
  check.report_revision_cache = {
    list,
    companions: [wire.companions[0]],
    observed_at: wire.list.items[0].accepted_at,
  };
  assert.equal(
    verifyReportCache(check.report_revision_cache, check).companions.length,
    1,
  );
  assert.throws(() => reportArchiveRecords(check), /not saved on this device/);
  const shorter = clone(list);
  shorter.items.pop();
  shorter.items[0]!.next_revision_id = null;
  shorter.latest_revision_id = shorter.items[0]!.revision_id;
  assert.throws(
    () => beginReportRefresh(shorter, check, shorter.items[0]!.accepted_at),
    /disappeared or changed/,
  );
  check.report_revision_cache.companions = verifyReportChain(
    wire.companions,
    check,
  );
  assert.equal(reportArchiveRecords(check).index.items.length, 2);
});
test("separate report archive index validates file path, parent, descriptor/result/full-file hashes and complete sequence", () => {
  const { check } = fixture();
  check.report_revision_cache = {
    list: wire.list,
    companions: wire.companions,
    observed_at: wire.list.items[1].accepted_at,
  };
  const { index, records } = reportArchiveRecords(check),
    sizes = Object.fromEntries(
      Object.entries(records).map(([p, v]) => [
        p,
        utf8(canonicalJson(v)).length,
      ]),
    );
  assert.equal(
    verifyReportArchiveIndex(index, check, records, sizes).length,
    2,
  );
  for (const mutate of [
    (v: any) => {
      v.data_generation++;
    },
    (v: any) => {
      v.items.reverse();
    },
    (v: any) => {
      v.items[0].path = `report-revisions/${randomUUID()}/${v.items[0].revision_id}.json`;
    },
    (v: any) => {
      v.items[0].result_sha256 = "a".repeat(64);
    },
    (v: any) => {
      v.items[0].size_bytes++;
    },
  ]) {
    const value = clone(index);
    mutate(value);
    assert.throws(() => verifyReportArchiveIndex(value, check, records, sizes));
  }
});
test("detail rejects a changing navigation chain without overwriting the immutable original", () => {
  const { check } = fixture(),
    detail = clone(wire.details[0]);
  detail.next_revision_id = randomUUID();
  assert.throws(
    () =>
      parseReportDetail(detail, check, parseReportList(wire.list, check), []),
    /changed during loading/,
  );
});
