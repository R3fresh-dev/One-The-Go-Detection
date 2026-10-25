import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { spawnSync } from "node:child_process";
import { fileURLToPath, URL } from "node:url";

const root = fileURLToPath(new URL("../", import.meta.url));
const workflow = readFileSync(
  new URL(
    "../../../.github/workflows/hosted-native-preview.yml",
    import.meta.url,
  ),
  "utf8",
);
const section = workflow.match(/^env:\n([\s\S]*?)\njobs:/m);
assert.ok(section, "Actual hosted preview workflow must declare its build env");
const previewEnvironment = Object.fromEntries(
  section[1]!
    .trim()
    .split("\n")
    .map((line) => {
      const entry = line.trim().match(/^([A-Z_]+): (.+)$/);
      assert.ok(
        entry,
        "Preview environment fixture must remain fully understood",
      );
      return [entry[1]!, entry[2]!.replace(/^'|'$/g, "")];
    }),
);

function child(program: string, unitPreview?: string) {
  const env = { ...process.env, ...previewEnvironment };
  delete env.EXPO_PUBLIC_APP_ENV;
  delete env.EXPO_PUBLIC_SERVERLESS;
  if (unitPreview === undefined) delete env.OTGD_UNIT_PREVIEW;
  else env.OTGD_UNIT_PREVIEW = unitPreview;
  const outcome = spawnSync(
    process.execPath,
    ["--import", "tsx", "-e", program],
    {
      cwd: root,
      env,
      encoding: "utf8",
      timeout: 15_000,
    },
  );
  assert.equal(outcome.error, undefined);
  assert.equal(outcome.status, 0, outcome.stderr || outcome.stdout);
  return JSON.parse(outcome.stdout);
}

for (const preview of [false, true]) {
  test(`actual hosted workflow env cannot replace the ${preview ? "guest" : "ordinary"} unit binary's explicit fictional OAuth identity`, () => {
    const result = child(
      `require('./tests/support/runtime.cjs');
       const { BUILD, validateBuild } = require('./src/platform/config.ts');
       validateBuild();
       console.log(JSON.stringify({ build: BUILD,
         ambientOrigin: process.env.EXPO_PUBLIC_OAUTH_ORIGIN,
         ambientCallback: process.env.EXPO_PUBLIC_OAUTH_WEB_CALLBACK_URI }));`,
      String(preview),
    );
    assert.equal(result.build.environment, preview ? "local" : "test");
    assert.equal(result.build.hostedPreview, preview);
    assert.equal(result.build.issuer, "http://localhost:8081");
    assert.equal(result.build.oauthOrigin, "http://localhost:8081");
    assert.equal(result.build.clientId, "otgd-local-mobile");
    assert.equal(result.build.apiUrl, "http://localhost:8000");
    assert.deepEqual(result.build.redirectUris, [
      "otgd-local://oauth/callback",
      "http://localhost:8082/",
    ]);
    // Isolation belongs to the test adapter, never an ambient build override.
    assert.equal(result.ambientOrigin, "https://unavailable.invalid");
    assert.equal(result.ambientCallback, "https://unavailable.invalid/");
  });
}

test("the actual hosted artifact config retains disabled pins outside the unit adapter", () => {
  const result = child(
    `const configure = require('./app.config.ts').default;
     console.log(JSON.stringify(configure({ config: {} }).extra));`,
  );
  assert.equal(result.environment, "local");
  assert.equal(result.hostedPreview, true);
  assert.equal(result.apiUrl, "https://unavailable.invalid");
  assert.equal(result.issuer, "https://unavailable.invalid");
  assert.equal(result.clientId, "otgd-hosted-fictional");
  assert.equal(result.oauthOrigin, "https://unavailable.invalid");
  assert.deepEqual(result.redirectUris, [
    "otgd-local://oauth/callback",
    "https://unavailable.invalid/",
  ]);
});
