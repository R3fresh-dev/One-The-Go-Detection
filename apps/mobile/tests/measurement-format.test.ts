import test from "node:test";
import assert from "node:assert/strict";
import { formatSalivaMeasurement } from "../src/ui/measurement-format";
import type { JsonObject } from "../src/core/types";

const base: JsonObject = {
  analyte: "OH11_THC",
  qualifier: "below_loq",
  value_ng_ml: null,
  limits: { lod_ng_ml: 0.001, loq_ng_ml: 0.003, upper_ng_ml: 250 },
  original_report: {
    value: null,
    unit: "pg/mL",
    qualifier: "below quantification limit",
  },
  collected_at: "2026-10-11T15:00:00.000Z",
  measured_at: "2026-10-11T16:00:00.000Z",
  assay_basis: "total_after_hydrolysis",
  concentration_basis: "collected_mixture",
  correction_status: "laboratory_corrected",
  source: "reference_lab",
};
test("below LOQ displays the supplied bound without creating a concentration or rounding it to zero", () => {
  const before = JSON.stringify(base),
    display = formatSalivaMeasurement(base);
  assert.equal(display.name, "11-hydroxy-THC");
  assert.equal(display.title, "Below quantification limit (<0.003 ng/mL)");
  assert.equal(JSON.stringify(base), before);
  assert.equal(base.value_ng_ml, null);
  assert.equal(
    display.facts.find((f) => f.label === "Detection limit (LOD)")!.value,
    "0.001 ng/mL",
  );
});
test("missing limits produce a qualifier without an invented cutoff", () => {
  for (const qualifier of ["below_loq", "not_detected", "above_range"]) {
    const display = formatSalivaMeasurement({
      ...base,
      qualifier,
      limits: { lod_ng_ml: null, loq_ng_ml: null, upper_ng_ml: null },
    });
    assert.ok(!display.title.includes("ng/mL"));
    assert.equal(
      display.facts.find((f) => f.label === "Quantification limit (LOQ)")!
        .value,
      "Not reported",
    );
  }
});
test("every supported censored/missing qualifier has distinct human-readable semantics", () => {
  const titles = Object.fromEntries(
    ["below_loq", "above_range", "not_detected", "not_measured", "invalid"].map(
      (qualifier) => [
        qualifier,
        formatSalivaMeasurement({ ...base, qualifier }).title,
      ],
    ),
  );
  assert.equal(titles.above_range, "Above reportable range (>250 ng/mL)");
  assert.equal(titles.not_detected, "Not detected (<0.001 ng/mL)");
  assert.equal(titles.not_measured, "Not measured");
  assert.equal(titles.invalid, "Invalid measurement");
  assert.equal(new Set(Object.values(titles)).size, 5);
});
test("only quantified results display a numeric concentration, preserving a real zero if reported", () => {
  assert.equal(
    formatSalivaMeasurement({
      ...base,
      qualifier: "quantified",
      value_ng_ml: 12.125,
    }).title,
    "12.125 ng/mL",
  );
  assert.equal(
    formatSalivaMeasurement({
      ...base,
      qualifier: "quantified",
      value_ng_ml: 0,
    }).title,
    "0 ng/mL",
  );
  assert.equal(
    formatSalivaMeasurement({
      ...base,
      qualifier: "quantified",
      value_ng_ml: null,
    }).title,
    "Numeric result unavailable",
  );
  assert.equal(
    formatSalivaMeasurement({
      ...base,
      qualifier: "future_qualifier",
      value_ng_ml: 99,
    }).title,
    "Unsupported measurement qualifier",
  );
});
test("original report units, laboratory correction, matrix and separate times remain visible", () => {
  const display = formatSalivaMeasurement({
    ...base,
    original_report: { value: 12500, unit: "pg/mL", qualifier: "quantified" },
  });
  const fields = Object.fromEntries(
    display.facts.map((f) => [f.label, f.value]),
  );
  assert.equal(fields["Original report value / unit"], "12500 pg/mL");
  assert.equal(fields["Original report qualifier"], "quantified");
  assert.equal(
    fields["Matrix / concentration basis"],
    "Collected oral-fluid mixture",
  );
  assert.equal(
    fields["Dilution correction"],
    "Corrected by reporting laboratory",
  );
  assert.equal(fields["Assay basis"], "Total after hydrolysis");
  assert.equal(fields["Collected (UTC)"], base.collected_at);
  assert.equal(fields["Measured (UTC)"], base.measured_at);
});
