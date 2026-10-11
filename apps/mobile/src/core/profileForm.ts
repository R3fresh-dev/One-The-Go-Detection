import { clone, IntegrityError } from "./integrity";
import { normalizeProfile } from "./domain";
import type { ProfileEnvelope } from "./types";

export type ProfileField =
  "age" | "height" | "feet" | "inches" | "weight" | "sleep" | "lastUse";
export interface ProfileFields {
  age: string;
  height: string;
  feet: string;
  inches: string;
  weight: string;
  sleep: string;
  lastUse: string;
  units: "metric" | "imperial";
}
export type ProfileErrors = Partial<Record<ProfileField, string>>;

export function localeDecimal(locale: string): string {
  return (
    new Intl.NumberFormat(locale)
      .formatToParts(1.1)
      .find((p) => p.type === "decimal")?.value ?? "."
  );
}
export function parseLocaleDecimal(
  text: string,
  label: string,
  locale: string,
  decimalPlaces?: number,
): number | null {
  let input = text.trim();
  if (!input) return null;
  const formatter = new Intl.NumberFormat(locale, { useGrouping: false });
  for (let number = 0; number <= 9; number++)
    input = input.split(formatter.format(number)).join(String(number));
  const decimal = localeDecimal(locale);
  if (decimal !== ".") input = input.split(decimal).join(".");
  if (
    !/^(?:\d+(?:\.\d*)?|\.\d+)$/.test(input) ||
    !Number.isFinite(Number(input))
  )
    throw new IntegrityError(
      "INVALID_NUMBER",
      `${label}: enter a number using “${decimal}” for decimals, without digit grouping, or leave it blank.`,
    );
  if (
    decimalPlaces !== undefined &&
    (input.split(".")[1]?.length ?? 0) > decimalPlaces
  )
    throw new IntegrityError(
      "NUMBER_PRECISION",
      `${label}: use ${decimalPlaces === 0 ? "a whole number" : `at most ${decimalPlaces} decimal place${decimalPlaces === 1 ? "" : "s"}`}.`,
    );
  return Number(input);
}
export function formatLocaleNumber(
  value: number | null,
  locale: string,
  decimals = 2,
): string {
  return value === null
    ? ""
    : new Intl.NumberFormat(locale, {
        useGrouping: false,
        maximumFractionDigits: decimals,
      }).format(value);
}

/** UI bounds are entry guardrails. They do not determine scientific eligibility. */
export function validateProfileFields(
  base: ProfileEnvelope,
  fields: ProfileFields,
  locale: string,
  now: string,
  canonical: { heightCm?: number | null; weightKg?: number | null } = {},
): { profile: ProfileEnvelope | null; errors: ProfileErrors } {
  const errors: ProfileErrors = {},
    next = clone(base);
  const number = (field: ProfileField, label: string, places?: number) => {
    try {
      return parseLocaleDecimal(fields[field], label, locale, places);
    } catch (error) {
      errors[field] =
        error instanceof Error ? error.message : "Review this number.";
      return null;
    }
  };
  const age = number("age", "Age", 0);
  if (age !== null && (age < 18 || age > 125))
    errors.age = "Age must be a whole number from 18 to 125, or blank.";
  next.profile.age_years = age;
  if (canonical.heightCm !== undefined)
    next.profile.height_cm = canonical.heightCm;
  else if (fields.units === "metric") {
    const height = number("height", "Height", 1);
    if (height !== null && (height <= 0 || height > 300))
      errors.height =
        "Height must be greater than 0 and at most 300 cm, or blank.";
    next.profile.height_cm = height;
  } else {
    const feet = number("feet", "Height in feet", 0),
      inches = number("inches", "Additional inches", 2);
    if ((feet === null) !== (inches === null) && !errors.feet && !errors.inches)
      errors[feet === null ? "feet" : "inches"] =
        "Enter both feet and additional inches, or leave both blank. Use 0 when needed.";
    if (inches !== null && (inches < 0 || inches >= 12))
      errors.inches = "Additional inches must be at least 0 and less than 12.";
    const height =
      feet === null || inches === null ? null : (feet * 12 + inches) * 2.54;
    if (height !== null && (height <= 0 || height > 300))
      errors.feet =
        "Combined height must be greater than 0 and at most 300 cm (118.11 in).";
    next.profile.height_cm = height;
  }
  if (canonical.weightKg !== undefined)
    next.profile.weight_kg = canonical.weightKg;
  else {
    const weight = number("weight", "Weight", 2),
      kg =
        weight === null
          ? null
          : fields.units === "imperial"
            ? weight * 0.45359237
            : weight;
    if (kg !== null && (kg <= 0 || kg > 500))
      errors.weight =
        "Weight must be greater than 0 and at most 500 kg (1102.31 lb), or blank.";
    next.profile.weight_kg = kg;
  }
  const sleep = number("sleep", "Sleep");
  if (sleep !== null && (sleep < 0 || sleep > 24))
    errors.sleep = "Sleep must be between 0 and 24 hours, or blank.";
  next.history.sleep_hours = sleep;
  next.context.last_use_at =
    next.context.last_use_status === "known" ? fields.lastUse.trim() : null;
  if (next.context.last_use_status === "known") {
    const value = fields.lastUse.trim(),
      matched =
        /^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$/.exec(
          value,
        ),
      time = Date.parse(value);
    if (!matched || !Number.isFinite(time))
      errors.lastUse = "Enter a complete date and time with a UTC offset or Z.";
    else {
      const year = Number(matched[1]),
        month = Number(matched[2]),
        day = Number(matched[3]),
        calendar = new Date(0);
      calendar.setUTCFullYear(year, month, 0);
      if (
        month < 1 ||
        month > 12 ||
        day < 1 ||
        day > calendar.getUTCDate() ||
        Number(matched[4]) > 23 ||
        Number(matched[5]) > 59 ||
        Number(matched[6]) > 59
      )
        errors.lastUse = "Enter a valid calendar date and time.";
      else if (time > Date.parse(now))
        errors.lastUse =
          "Choose a last-use date and time that is not in the future.";
    }
  }
  if (Object.keys(errors).length) return { profile: null, errors };
  return { profile: normalizeProfile(next, now), errors };
}
