import Ajv2020 from "ajv/dist/2020";
import addFormats from "ajv-formats";
import companionSchema from "../contracts/ReportRevisionCompanion.schema.json";
import listSchema from "../contracts/ReportRevisionList.schema.json";
import detailSchema from "../contracts/ReportRevisionDetail.schema.json";
import indexSchema from "../contracts/ReportRevisionIndex.schema.json";
import measurementSchema from "../contracts/measurement.schema.json";
import {
  assertBytes,
  canonicalJson,
  clone,
  digest,
  IntegrityError,
  utf8,
} from "./integrity";
import { verifyCheck, verifyResult } from "./domain";
import type {
  CheckRecord,
  JsonObject,
  MeasurementResult,
  Source,
} from "./types";

export interface ReportResult {
  schema_version: "1.0.0";
  result_kind: "administrative_report_result";
  result_id: string;
  session_id: string;
  revision_id: string;
  revision_sha256: string;
  base_snapshot_sha256: string;
  target_at: string;
  evaluated_at: string;
  state: MeasurementResult["state"];
  reason_codes: string[];
  provenance_summary: Source[];
  replaces_result_id: string;
  inference_available: false;
  probability: null;
  classification: null;
  model_id: null;
}
export interface ReportCompanion {
  schema_version: "1.0.0";
  record_type: "administrative_report_revision";
  revision_id: string;
  session_id: string;
  data_generation: number;
  sequence: number;
  accepted_at: string;
  descriptor: {
    schema_version: "1.0.0";
    revision_id: string;
    session_id: string;
    data_generation: number;
    base_snapshot_sha256: string;
    base_evidence_sha256: string;
    previous_revision_id: string | null;
    previous_revision_sha256: string | null;
    original_target_at: string;
    original_collected_at: string;
    original_capture_completed_at: string;
    report: {
      kind: "correction" | "reanalysis";
      reason_code: "CORRECTED_LABORATORY_REPORT" | "SPECIMEN_REANALYSIS";
      reported_at: string;
      replacement_measurements: JsonObject[];
      source_report: {
        artifact_id: string;
        version_id: string;
        sha256: string;
        media_type: "application/pdf";
        size_bytes: number;
      };
      authorization: {
        operator_account_ref: string;
        study_id: string;
        protocol_id: string;
        configuration_id: string;
        configuration_sha256: string;
        consent_record_id: string;
        retention_policy_id: string;
        approved_lab_methods: Record<
          string,
          { calibration_ids: string[]; instrument_ids: string[] }
        >;
      };
    };
  };
  revision_sha256: string;
  effective_measurements: JsonObject[];
  result: ReportResult;
  result_sha256: string;
}
export interface ReportSummary {
  revision_id: string;
  revision_sha256: string;
  sequence: number;
  kind: "correction" | "reanalysis";
  reported_at: string;
  accepted_at: string;
  previous_revision_id: string | null;
  next_revision_id: string | null;
  result_id: string;
  result_state: MeasurementResult["state"];
}
export interface ReportList {
  schema_version: "1.0.0";
  session_id: string;
  data_generation: number;
  base_snapshot_sha256: string;
  base_result_id: string;
  original_target_at: string;
  original_collected_at: string | null;
  original_capture_completed_at: string;
  latest_revision_id: string | null;
  items: ReportSummary[];
}
export interface ReportDetail {
  schema_version: "1.0.0";
  session_id: string;
  data_generation: number;
  revision: ReportCompanion;
  previous_revision_id: string | null;
  next_revision_id: string | null;
}
export interface ReportCache {
  list: ReportList;
  companions: ReportCompanion[];
  observed_at: string;
}
export interface ReportIndex {
  schema_version: "1.0.0";
  session_id: string;
  data_generation: number;
  base_snapshot_sha256: string;
  items: {
    revision_id: string;
    sequence: number;
    revision_sha256: string;
    result_id: string;
    result_sha256: string;
    path: string;
    sha256: string;
    size_bytes: number;
  }[];
}
const ajv = new Ajv2020({ strict: false, allErrors: true });
addFormats(ajv);
const validateCompanion = ajv.compile(companionSchema),
  validateList = ajv.compile(listSchema),
  validateDetail = ajv.compile(detailSchema),
  validateIndex = ajv.compile(indexSchema),
  validateMeasurement = ajv.compile(measurementSchema);
const fail = (message: string): never => {
  throw new IntegrityError("REPORT_REVISION_INTEGRITY", message);
};
const equal = (a: unknown, b: unknown) => digest(a) === digest(b);
const sortedUnique = (values: string[]) => [...new Set(values)].sort();
const reason = {
  correction: "CORRECTED_LABORATORY_REPORT",
  reanalysis: "SPECIMEN_REANALYSIS",
} as const;
function instant(value: string): number {
  const result = Date.parse(value);
  if (
    !Number.isFinite(result) ||
    !/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$/.test(value) ||
    new Date(result).toISOString().slice(0, 19) !== value.slice(0, 19)
  )
    fail("A laboratory report timestamp is not a real UTC instant.");
  return result;
}

function original(check: CheckRecord): MeasurementResult {
  if (
    !check.frozen ||
    !check.result ||
    !check.snapshot_sha256 ||
    !check.evidence_sha256
  )
    fail(
      "The original captured record and original result must be available before laboratory report history can be verified.",
    );
  verifyCheck(check);
  return verifyResult(check.result, check);
}
function hasBaseIdentity(
  check: CheckRecord,
  value: {
    session_id: string;
    data_generation: number;
    base_snapshot_sha256: string;
  },
): boolean {
  return (
    value.session_id === check.id &&
    value.data_generation === check.generation &&
    value.base_snapshot_sha256 === check.snapshot_sha256
  );
}
export function parseReportList(
  value: unknown,
  check: CheckRecord,
): ReportList {
  assertBytes(value, 524_288);
  if (!validateList(value))
    fail(
      "Laboratory report history uses an unsupported version or record shape.",
    );
  const list = value as ReportList,
    base = original(check),
    snapshot = check.snapshot;
  if (
    !hasBaseIdentity(check, list) ||
    list.base_result_id !== base.result_id ||
    list.original_target_at !== snapshot.target_at ||
    list.original_collected_at !== snapshot.sample.collected_at ||
    list.original_capture_completed_at !== snapshot.capture_completed_at ||
    list.latest_revision_id !== (list.items.at(-1)?.revision_id ?? null)
  )
    fail(
      "Laboratory report history does not match the original captured record or active data generation.",
    );
  const ids = new Set<string>(),
    resultIds = new Set([base.result_id]);
  for (const [i, entry] of list.items.entries()) {
    instant(entry.reported_at);
    instant(entry.accepted_at);
    if (
      ids.has(entry.revision_id) ||
      resultIds.has(entry.result_id) ||
      entry.sequence !== i + 1 ||
      entry.previous_revision_id !== (list.items[i - 1]?.revision_id ?? null) ||
      entry.next_revision_id !== (list.items[i + 1]?.revision_id ?? null)
    )
      fail("Laboratory report history is incomplete, cyclic or out of order.");
    ids.add(entry.revision_id);
    resultIds.add(entry.result_id);
  }
  if (
    list.items.length &&
    (snapshot.mode === "synthetic" ||
      snapshot.sample.status === "not_collected" ||
      snapshot.sample.collected_at === null)
  )
    fail(
      "An uncollected or synthetic specimen cannot gain a laboratory report.",
    );
  return clone(list);
}

function verifyReading(reading: JsonObject): void {
  if (!validateMeasurement(reading))
    fail(
      "A revised analyte does not match the supported measurement contract.",
    );
  const limits = reading.limits as JsonObject,
    lod = limits.lod_ng_ml,
    loq = limits.loq_ng_ml,
    upper = limits.upper_ng_ml;
  if (
    (typeof lod === "number" && typeof loq === "number" && lod > loq) ||
    (typeof loq === "number" && typeof upper === "number" && loq > upper) ||
    (typeof lod === "number" && typeof upper === "number" && lod > upper)
  )
    fail("A laboratory report has inconsistent analytical limits.");
  if (reading.qualifier === "quantified") {
    const amount = reading.value_ng_ml as number,
      raw = reading.original_report as JsonObject,
      converted = raw.unit === "pg/mL" ? Number(raw.value) / 1000 : raw.value;
    if (
      typeof raw.value !== "number" ||
      typeof converted !== "number" ||
      Math.abs(converted - amount) >
        Math.max(
          1e-12,
          1e-9 * Math.max(Math.abs(converted), Math.abs(amount)),
        ) ||
      amount < Number(loq) ||
      amount > Number(upper)
    )
      fail(
        "The normalized value does not preserve the laboratory report or analytical range.",
      );
  }
}

export function verifyReportChain(
  values: unknown[],
  check: CheckRecord,
): ReportCompanion[] {
  if (values.length > 20)
    fail("Laboratory report history exceeds the supported revision limit.");
  if (!values.length) return [];
  const base = original(check),
    snapshot = check.snapshot;
  if (
    snapshot.mode === "synthetic" ||
    snapshot.sample.status === "not_collected" ||
    snapshot.sample.collected_at === null
  )
    fail("A laboratory report requires the original collected specimen.");
  const measurementIds = new Set<string>(),
    revisionIds = new Set<string>(),
    resultIds = new Set([base.result_id]);
  let effective = new Map<string, JsonObject>();
  for (const measurement of snapshot.saliva) {
    verifyReading(measurement);
    if (
      measurementIds.has(String(measurement.measurement_id)) ||
      effective.has(String(measurement.analyte))
    )
      fail("The original analytical identities are duplicated.");
    measurementIds.add(String(measurement.measurement_id));
    effective.set(String(measurement.analyte), measurement);
  }
  const verified: ReportCompanion[] = [];
  for (const [i, value] of values.entries()) {
    assertBytes(value, 524_288);
    if (!validateCompanion(value))
      fail(
        "A laboratory report uses an unsupported companion version or field.",
      );
    const item = value as ReportCompanion,
      d = item.descriptor,
      report = d.report,
      authorization = report.authorization,
      previous = verified[i - 1];
    instant(item.accepted_at);
    instant(report.reported_at);
    instant(item.result.evaluated_at);
    if (
      item.session_id !== check.id ||
      item.data_generation !== check.generation ||
      item.sequence !== i + 1 ||
      item.revision_id !== d.revision_id ||
      revisionIds.has(item.revision_id) ||
      !hasBaseIdentity(check, d) ||
      d.base_evidence_sha256 !== check.evidence_sha256 ||
      d.original_target_at !== snapshot.target_at ||
      d.original_collected_at !== snapshot.sample.collected_at ||
      d.original_capture_completed_at !== snapshot.capture_completed_at ||
      d.previous_revision_id !== (previous?.revision_id ?? null) ||
      d.previous_revision_sha256 !== (previous?.revision_sha256 ?? null) ||
      digest(d) !== item.revision_sha256 ||
      digest(item.result) !== item.result_sha256
    )
      fail(
        "A laboratory report differs from its immutable identity, original evidence or predecessor.",
      );
    if (
      report.reason_code !== reason[report.kind] ||
      report.source_report.version_id === "null" ||
      authorization.operator_account_ref !== snapshot.subject_ref ||
      authorization.study_id !== snapshot.study_id ||
      authorization.protocol_id !== snapshot.protocol_id ||
      Date.parse(report.reported_at) <
        Date.parse(snapshot.sample.collected_at!) ||
      Date.parse(report.reported_at) > Date.parse(item.accepted_at) + 60_000 ||
      Date.parse(item.accepted_at) <
        Date.parse(previous?.accepted_at ?? snapshot.capture_completed_at)
    )
      fail("Laboratory report provenance or chronology is inconsistent.");
    const usedMethods = new Set<string>(),
      changed = new Set<string>();
    for (const reading of report.replacement_measurements) {
      verifyReading(reading);
      const measurementId = String(reading.measurement_id),
        analyte = String(reading.analyte);
      if (
        reading.source !== "reference_lab" ||
        reading.sample_id !== snapshot.sample.sample_id ||
        reading.collected_at !== snapshot.sample.collected_at ||
        measurementIds.has(measurementId) ||
        changed.has(analyte)
      )
        fail(
          "A revised measurement changes specimen identity or reuses analytical evidence.",
        );
      if (reading.qualifier !== "not_measured") {
        const method =
            typeof reading.method_id === "string" ? reading.method_id : "",
          approval = authorization.approved_lab_methods[method];
        if (
          !approval ||
          !approval.calibration_ids.includes(String(reading.calibration_id)) ||
          !approval.instrument_ids.includes(String(reading.instrument_id)) ||
          !equal(
            sortedUnique(approval.calibration_ids),
            approval.calibration_ids,
          ) ||
          !equal(
            sortedUnique(approval.instrument_ids),
            approval.instrument_ids,
          ) ||
          typeof reading.measured_at !== "string" ||
          Date.parse(reading.measured_at) <
            Date.parse(snapshot.sample.collected_at!) ||
          Date.parse(reading.measured_at) > Date.parse(report.reported_at)
        )
          fail(
            "A revised measurement lacks matching approved method provenance or an analytical time.",
          );
        usedMethods.add(method);
      }
      changed.add(analyte);
      measurementIds.add(measurementId);
      effective.set(analyte, reading);
    }
    if (
      !equal(
        [...usedMethods].sort(),
        Object.keys(authorization.approved_lab_methods).sort(),
      )
    )
      fail("Laboratory method provenance contains unused or missing methods.");
    const measurements = [...effective]
        .sort(([a], [b]) => a.localeCompare(b, "en"))
        .map(([, m]) => m),
      invalid = measurements.some((m) => m.qualifier === "invalid"),
      result = item.result;
    const expectedState =
      base.state === "invalid" || invalid
        ? "invalid"
        : base.state === "inconclusive"
          ? "inconclusive"
          : "measurement_only";
    const expectedReasons = sortedUnique([
      ...base.reason_codes,
      report.reason_code,
      ...(invalid ? ["INVALID_ANALYTICAL_REPORT"] : []),
    ]);
    const sources = sortedUnique([
      ...measurements.map((m) => String(m.source)),
      snapshot.eyes.source,
      snapshot.cardiac.source,
      snapshot.task.source,
    ]);
    if (
      !equal(measurements, item.effective_measurements) ||
      result.session_id !== check.id ||
      result.revision_id !== item.revision_id ||
      result.revision_sha256 !== item.revision_sha256 ||
      result.base_snapshot_sha256 !== check.snapshot_sha256 ||
      result.target_at !== snapshot.target_at ||
      result.replaces_result_id !==
        (previous?.result.result_id ?? base.result_id) ||
      resultIds.has(result.result_id) ||
      result.state !== expectedState ||
      !equal(result.reason_codes, expectedReasons) ||
      !equal(result.provenance_summary, sources) ||
      result.evaluated_at !== item.accepted_at
    )
      fail(
        "A revised report result changes original timing, suppresses invalidity, or differs from its analytical evidence.",
      );
    revisionIds.add(item.revision_id);
    resultIds.add(result.result_id);
    verified.push(clone(item));
  }
  return verified;
}

function summaryMatches(
  item: ReportCompanion,
  summary: ReportSummary,
): boolean {
  return (
    item.revision_id === summary.revision_id &&
    item.revision_sha256 === summary.revision_sha256 &&
    item.sequence === summary.sequence &&
    item.accepted_at === summary.accepted_at &&
    item.descriptor.report.kind === summary.kind &&
    item.descriptor.report.reported_at === summary.reported_at &&
    item.descriptor.previous_revision_id === summary.previous_revision_id &&
    item.result.result_id === summary.result_id &&
    item.result.state === summary.result_state
  );
}
export function parseReportDetail(
  value: unknown,
  check: CheckRecord,
  list: ReportList,
  prior: ReportCompanion[],
): ReportCompanion {
  assertBytes(value, 1_048_576);
  if (!validateDetail(value))
    fail("The laboratory report detail uses an unsupported record shape.");
  const detail = value as ReportDetail,
    item = detail.revision,
    summary = list.items[prior.length];
  if (
    detail.session_id !== check.id ||
    detail.data_generation !== check.generation ||
    !summary ||
    !summaryMatches(item, summary) ||
    detail.previous_revision_id !== summary.previous_revision_id ||
    detail.next_revision_id !== summary.next_revision_id
  )
    fail(
      "Report history changed during loading. Refresh its complete history before opening or exporting it.",
    );
  return verifyReportChain([...prior, item], check).at(-1)!;
}
export function verifyReportCache(
  cache: ReportCache,
  check: CheckRecord,
  complete = false,
): ReportCache {
  const list = parseReportList(cache.list, check),
    companions = verifyReportChain(cache.companions, check);
  if (
    companions.length > list.items.length ||
    companions.some((item, i) => !summaryMatches(item, list.items[i]!))
  )
    fail(
      "Cached laboratory report details do not match their verified history.",
    );
  if (complete && companions.length !== list.items.length)
    throw new IntegrityError(
      "REPORT_CACHE_INCOMPLETE",
      "Some laboratory report revisions are not saved on this device. Refresh laboratory reports while connected before exporting this selection; no revisions were omitted.",
    );
  return { list, companions, observed_at: cache.observed_at };
}
export function beginReportRefresh(
  list: ReportList,
  check: CheckRecord,
  observedAt: string,
): ReportCache {
  const prior = check.report_revision_cache
    ? verifyReportCache(check.report_revision_cache, check)
    : null;
  if (
    prior &&
    (prior.list.items.length > list.items.length ||
      prior.list.items.some(
        (item, i) =>
          item.revision_id !== list.items[i]?.revision_id ||
          item.revision_sha256 !== list.items[i]?.revision_sha256,
      ))
  )
    fail(
      "Previously verified laboratory history disappeared or changed. The cached original evidence was retained.",
    );
  return { list, companions: prior?.companions ?? [], observed_at: observedAt };
}
export function reportArchiveRecords(check: CheckRecord): {
  index: ReportIndex;
  records: Record<string, ReportCompanion>;
} {
  const companions = check.report_revision_cache
    ? verifyReportCache(check.report_revision_cache, check, true).companions
    : [];
  const records: Record<string, ReportCompanion> = {},
    index: ReportIndex = {
      schema_version: "1.0.0",
      session_id: check.id,
      data_generation: check.generation,
      base_snapshot_sha256: check.snapshot_sha256!,
      items: [],
    };
  for (const item of companions) {
    const path = `report-revisions/${check.id}/${item.revision_id}.json`,
      size = utf8(canonicalJson(item)).byteLength;
    records[path] = item;
    index.items.push({
      revision_id: item.revision_id,
      sequence: item.sequence,
      revision_sha256: item.revision_sha256,
      result_id: item.result.result_id,
      result_sha256: item.result_sha256,
      path,
      sha256: digest(item),
      size_bytes: size,
    });
  }
  assertBytes(index, 16_384);
  return { index, records };
}
export function verifyReportArchiveIndex(
  value: unknown,
  check: CheckRecord,
  records: Record<string, unknown>,
  fileSizes: Record<string, number>,
): string[] {
  assertBytes(value, 16_384);
  if (!validateIndex(value))
    fail("An exported report revision index has an unsupported shape.");
  const index = value as ReportIndex;
  if (!hasBaseIdentity(check, index))
    fail(
      "An exported report revision index belongs to another check or data generation.",
    );
  const paths: string[] = [],
    values: unknown[] = [];
  for (const [i, entry] of index.items.entries()) {
    const path = `report-revisions/${check.id}/${entry.revision_id}.json`,
      value = records[path];
    if (
      entry.sequence !== i + 1 ||
      entry.path !== path ||
      paths.includes(path) ||
      !value ||
      fileSizes[path] !== entry.size_bytes ||
      digest(value) !== entry.sha256
    )
      fail(
        "An exported report companion is missing, duplicated or differs from its indexed file.",
      );
    paths.push(path);
    values.push(value);
  }
  const verified = verifyReportChain(values, check);
  for (const [i, item] of verified.entries()) {
    const entry = index.items[i]!;
    if (
      entry.revision_id !== item.revision_id ||
      entry.revision_sha256 !== item.revision_sha256 ||
      entry.result_id !== item.result.result_id ||
      entry.result_sha256 !== item.result_sha256
    )
      fail(
        "An exported report revision index differs from its verified companion.",
      );
  }
  return paths;
}
