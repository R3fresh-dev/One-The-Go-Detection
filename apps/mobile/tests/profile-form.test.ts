import test from "node:test";
import assert from "node:assert/strict";
import { emptyProfile } from "../src/core/domain";
import {
  formatLocaleNumber,
  parseLocaleDecimal,
  validateProfileFields,
  type ProfileFields,
} from "../src/core/profileForm";

const at = "2026-10-11T12:00:00.000Z";
const blank: ProfileFields = {
  age: "",
  height: "",
  feet: "",
  inches: "",
  weight: "",
  sleep: "",
  lastUse: "",
  units: "metric",
};

test("locale decimal and digit input becomes locale-independent numbers", () => {
  assert.equal(parseLocaleDecimal("75,25", "Weight", "fr-FR", 2), 75.25);
  assert.equal(parseLocaleDecimal("١٧٥٫٥", "Height", "ar-EG", 1), 175.5);
  assert.equal(parseLocaleDecimal("75.25", "Weight", "en-US", 2), 75.25);
  assert.equal(parseLocaleDecimal("  ", "Age", "en-US", 0), null);
  for (const value of ["1,234.50", "1 234", "1e2", "Infinity", "-2"])
    assert.throws(() => parseLocaleDecimal(value, "Weight", "en-US", 2));
  assert.throws(
    () => parseLocaleDecimal("175,55", "Height", "fr-FR", 1),
    /at most 1/,
  );
});

test("profile validation collects independent inline errors without clearing draft text", () => {
  const fields = {
      ...blank,
      age: "17",
      height: "301",
      weight: "0",
      sleep: "25",
    },
    original = structuredClone(fields);
  const result = validateProfileFields(emptyProfile(at), fields, "en-US", at);
  assert.equal(result.profile, null);
  assert.deepEqual(Object.keys(result.errors), [
    "age",
    "height",
    "weight",
    "sleep",
  ]);
  assert.deepEqual(fields, original);
});

test("optional blank demographics stay null and unknown remains distinct from declined", () => {
  const base = emptyProfile(at);
  base.history.use_frequency = "declined";
  base.context.last_use_status = "declined";
  const result = validateProfileFields(base, blank, "en-US", at);
  assert.equal(result.profile?.profile.age_years, null);
  assert.equal(result.profile?.profile.bmi, null);
  assert.equal(result.profile?.history.use_frequency, "declined");
  assert.equal(result.profile?.context.last_use_status, "declined");
});

test("whole feet plus bounded inches and pounds use exact SI conversions", () => {
  const result = validateProfileFields(
    emptyProfile(at),
    { ...blank, units: "imperial", feet: "5", inches: "10", weight: "150" },
    "en-US",
    at,
  );
  assert.equal(result.profile?.profile.height_cm, 177.8);
  assert.equal(result.profile?.profile.weight_kg, 68.0388555);
  assert.ok(Math.abs(result.profile!.profile.bmi! - 21.52253815221916) < 1e-12);
  assert.ok(
    validateProfileFields(
      emptyProfile(at),
      { ...blank, units: "imperial", feet: "5", inches: "12" },
      "en-US",
      at,
    ).errors.inches,
  );
});

test("display rounding and repeated unit toggles preserve original canonical values", () => {
  const base = emptyProfile(at);
  base.profile.height_cm = 177.8;
  base.profile.weight_kg = 68.0388555;
  let profile = base;
  for (let index = 0; index < 25; index++) {
    const units = index % 2 ? "metric" : "imperial";
    const fields = {
      ...blank,
      units,
      height: formatLocaleNumber(profile.profile.height_cm, "fr-FR", 1),
      weight: formatLocaleNumber(
        units === "metric"
          ? profile.profile.weight_kg
          : profile.profile.weight_kg! / 0.45359237,
        "fr-FR",
        2,
      ),
      feet: "5",
      inches: "10",
    } as ProfileFields;
    profile = validateProfileFields(profile, fields, "fr-FR", at, {
      heightCm: profile.profile.height_cm,
      weightKg: profile.profile.weight_kg,
    }).profile!;
  }
  assert.equal(profile.profile.height_cm, 177.8);
  assert.equal(profile.profile.weight_kg, 68.0388555);
});

test("known last-use rejects impossible calendar dates and future times with a field error", () => {
  const base = emptyProfile(at);
  base.context.last_use_status = "known";
  assert.ok(
    validateProfileFields(
      base,
      { ...blank, lastUse: "2026-02-30T12:00:00Z" },
      "en-US",
      at,
    ).errors.lastUse,
  );
  assert.ok(
    validateProfileFields(
      base,
      { ...blank, lastUse: "2026-10-12T12:00:00Z" },
      "en-US",
      at,
    ).errors.lastUse,
  );
  const valid = validateProfileFields(
    base,
    { ...blank, lastUse: "2026-10-11T11:00:00+01:00" },
    "en-US",
    at,
  );
  assert.equal(valid.profile?.context.last_use_at, "2026-10-11T10:00:00.000Z");
  assert.equal(valid.profile?.history.time_since_use_min, 120);
});
