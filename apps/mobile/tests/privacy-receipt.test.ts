import test from "node:test";
import assert from "node:assert/strict";
import { buildSync } from "esbuild";
import { resolve } from "node:path";
import fixture from "../testfixtures/backend-privacy-deletion-receipt.json";
import { clone } from "../src/core/integrity";
import { parsePrivacyJob } from "../src/services/api";
const compiled = buildSync({
  entryPoints: [resolve("tests/support/privacy-rendering.tsx")],
  bundle: true,
  write: false,
  platform: "node",
  format: "cjs",
  resolveExtensions: [
    ".web.tsx",
    ".web.ts",
    ".web.js",
    ".tsx",
    ".ts",
    ".jsx",
    ".js",
    ".json",
  ],
  alias: { "react-native": resolve("e2e/fixtures/native-web-shim.js") },
  define: {
    __DEV__: "false",
    "process.env.EXPO_OS": '"web"',
    "process.env.NODE_ENV": '"test"',
    "process.env.EXPO_PUBLIC_APP_ENV": '"local"',
    "process.env.EXPO_PUBLIC_HOSTED_PREVIEW": '"false"',
  },
}).outputFiles![0]!.text;
const output = { exports: {} as any };
new Function("module", "exports", "require", compiled)(
  output,
  output.exports,
  require,
);
const render = (value: unknown) =>
  output.exports
    .renderPrivacyReceipt(value)
    .replace(/<[^>]*>/g, " ")
    .replace(/\s+/g, " ");

test("actual Python API deletion receipt survives client admission and JobCard rendering with all factual retention details", () => {
  const parsed = parsePrivacyJob(fixture);
  assert.deepEqual(parsed.retained_categories, fixture.retained_categories);
  const text = render(fixture);
  assert.equal(fixture.retained_categories.length, 6);
  for (const category of fixture.retained_categories) {
    assert.ok(text.includes(category.category), category.category);
    assert.ok(text.includes(category.policy_basis), category.policy_basis);
    assert.ok(text.includes(category.reason), category.reason);
  }
  assert.match(text, /No scheduled expiry supplied/);
  assert.doesNotMatch(
    text,
    /Retained category [1-6]|complete erasure confirmed/i,
  );
});
test("legacy category strings retain their real names and honestly disclose missing policy, reason and expiry", () => {
  const value = {
    ...clone(fixture),
    retained_categories: fixture.retained_categories.map(
      (entry) => entry.category,
    ),
  };
  const text = render(value);
  for (const category of value.retained_categories)
    assert.ok(text.includes(category));
  assert.match(
    text,
    /Legacy receipt: policy basis, retention reason and expiry were not supplied/,
  );
  assert.doesNotMatch(text, /Retained category [1-6]/);
});
test("supplied category expiry is displayed exactly and separately from the overall job expiry", () => {
  const value = clone(fixture);
  value.retained_categories[0]!.expires_at = "2027-02-28T23:59:59.123Z" as any;
  value.retained_categories[0]!.policy_basis = "fixture-specific-policy-basis";
  const text = render(value);
  assert.ok(text.includes("2027-02-28T23:59:59.123Z"));
  assert.ok(text.includes(value.retained_categories[0]!.policy_basis));
});
test("retention admission rejects malformed dates, nested arbitrary fields and unbounded category receipts", () => {
  const first = clone(fixture.retained_categories[0]!);
  for (const retained_categories of [
    [{ ...first, expires_at: "2027-02-30T00:00:00Z" }],
    [{ ...first, expires_at: "2027-01-01" }],
    [{ ...first, expires_at: { value: "2027-01-01T00:00:00Z" } }],
    [{ ...first, reason: { secret: "must not be stringified" } }],
    [{ ...first, category: ["identity"] }],
    [{ ...first, policy_basis: { invented: "authority" } }],
    [{ ...first, extra_payload: { hidden: true } }],
    [
      {
        category: first.category,
        policy_basis: first.policy_basis,
        reason: first.reason,
      },
    ],
    [" "],
    [{ ...first, reason: " " }],
    [null],
    ["x".repeat(257)],
    [{ ...first, policy_basis: "x".repeat(257) }],
    [{ ...first, reason: "x".repeat(1001) }],
    [{ ...first, expires_at: "2027-04-31T00:00:00Z" }],
    [{ ...first, expires_at: "2027-01-01T24:00:00Z" }],
    [{ ...first, expires_at: "2027-01-01T00:00:00+24:00" }],
    [""],
    Array(33).fill(first),
  ])
    assert.throws(
      () => parsePrivacyJob({ ...fixture, retained_categories }),
      JSON.stringify(retained_categories),
    );
});

test("valid leap days and offset expiry preserve exact supplied timestamps while display-boundary nested payloads fail", () => {
  for (const expires_at of [
    "2028-02-29T23:59:59.123Z",
    "2027-02-28T23:59:59+05:30",
  ]) {
    const value: any = clone(fixture);
    value.retained_categories[0].expires_at = expires_at;
    assert.equal(
      (parsePrivacyJob(value).retained_categories[0] as any).expires_at,
      expires_at,
    );
  }
  for (const change of [
    { accepted_at: { arbitrary: "payload" } },
    { expires_at: "2027-02-30T00:00:00Z" },
    { policy_version: { arbitrary: "payload" } },
    { scope: { kind: { arbitrary: "payload" } } },
    { failure_code: { arbitrary: "payload" } },
    { allowed_actions: Array(17).fill("refresh") },
  ])
    assert.throws(() => parsePrivacyJob({ ...fixture, ...change }));
});
