import { test, expect } from "@playwright/test";
import { buildSync } from "esbuild";
import { resolve } from "node:path";
import fixture from "../testfixtures/backend-raw-recordings.json";
import { clone } from "../src/core/integrity";
import { readFileSync } from "node:fs";
const rawExport = JSON.parse(
  readFileSync(
    resolve(
      "../../services/api/tests/fixtures/raw-export-v1/raw-export-scopes.json",
    ),
    "utf8",
  ),
);
const availabilityBundle = (hosted: boolean) =>
  buildSync({
    entryPoints: [resolve("e2e/fixtures/availability-component.tsx")],
    bundle: true,
    write: false,
    platform: "browser",
    format: "iife",
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
      "process.env.NODE_ENV": '"test"',
      "process.env.EXPO_PUBLIC_APP_ENV": '"local"',
      "process.env.EXPO_PUBLIC_HOSTED_PREVIEW": JSON.stringify(String(hosted)),
    },
    loader: { ".tsx": "tsx" },
  }).outputFiles![0]!.text;
const ordinaryAvailability = availabilityBundle(false),
  hostedAvailability = availabilityBundle(true);
const bundle = buildSync({
  entryPoints: [resolve("e2e/fixtures/raw-recording-component.tsx")],
  bundle: true,
  write: false,
  platform: "browser",
  format: "iife",
  alias: { "react-native": "react-native-web" },
  define: { "process.env.NODE_ENV": '"test"' },
  loader: { ".tsx": "tsx" },
}).outputFiles![0]!.text;

test.beforeEach(async ({ page }) => {
  await page.clock.install({ time: Date.parse("2026-10-11T12:00:00Z") });
  await page.goto("/");
  await page.setContent('<html><body><main id="root"></main></body></html>');
  await page.addScriptTag({ content: bundle });
});
const unaccepted = () => {
  const value = clone(fixture);
  value.receipt_id = null as any;
  value.preference_receipt = null as any;
  value.choices = {
    eye_video: { record: false, upload: false },
    ecg_waveform: { record: false, upload: false },
  };
  return value;
};

test("actual raw choices component defaults both optional purposes off and requires exact policy review before a separate local/upload choice", async ({
  page,
}) => {
  await page.evaluate(
    (value) => (window as any).renderRaw(value),
    unaccepted(),
  );
  const record = page.getByRole("switch", {
    name: "Record eye video on this device",
    exact: true,
  });
  const upload = page.getByRole("switch", {
    name: "Allow explicit upload of eye video",
    exact: true,
  });
  await expect(record).not.toBeChecked();
  await expect(upload).not.toBeChecked();
  await expect(upload).toBeDisabled();
  await expect(
    page.getByText("2 days from the first owned acquisition start", {
      exact: true,
    }),
  ).toBeVisible();
  const confirm = page.getByRole("button", {
    name: "Confirm separate recording and upload choices",
    exact: true,
  });
  await expect(confirm).toBeDisabled();
  await page
    .getByRole("button", {
      name: "Read complete raw recording notice",
      exact: true,
    })
    .click();
  await expect(
    page.getByText(fixture.policy.raw_notice.content, { exact: true }),
  ).toBeVisible();
  await page
    .getByRole("switch", {
      name: "I reviewed this exact raw recording notice and retention policy",
      exact: true,
    })
    .check();
  await record.check();
  await expect(upload).not.toBeChecked();
  await expect(upload).toBeEnabled();
  await confirm.click();
  await expect
    .poll(() => page.evaluate(() => (window as any).rawEvents))
    .toEqual([
      {
        kind: "save",
        choices: {
          eye_video: { record: true, upload: false },
          ecg_waveform: { record: false, upload: false },
        },
      },
    ]);
  await upload.check();
  await record.uncheck();
  await expect(upload).not.toBeChecked();
});

test("account or generation change resets unfinished choices and notice acknowledgment", async ({
  page,
}) => {
  const value = unaccepted();
  await page.evaluate(
    (value) => (window as any).renderRaw(value, "account-A:g1"),
    value,
  );
  await page
    .getByRole("button", {
      name: "Read complete raw recording notice",
      exact: true,
    })
    .click();
  await page
    .getByRole("switch", {
      name: "I reviewed this exact raw recording notice and retention policy",
      exact: true,
    })
    .check();
  await page
    .getByRole("switch", {
      name: "Record ecg waveform on this device",
      exact: true,
    })
    .check();
  await page.evaluate(
    (value) => (window as any).renderRaw(value, "account-B:g2"),
    value,
  );
  await expect(
    page.getByRole("switch", {
      name: "Record ecg waveform on this device",
      exact: true,
    }),
  ).not.toBeChecked();
  await expect(
    page.getByRole("switch", {
      name: "I reviewed this exact raw recording notice and retention policy",
      exact: true,
    }),
  ).not.toBeChecked();
  await expect(
    page.getByRole("button", {
      name: "Confirm separate recording and upload choices",
      exact: true,
    }),
  ).toBeDisabled();
  await expect(
    page.getByRole("button", {
      name: "Read complete raw recording notice",
      exact: true,
    }),
  ).toBeVisible();
});

test("local revocation fence overrides old confirmed grant without claiming cleanup completion", async ({
  page,
}) => {
  await page.evaluate(
    (value) => (window as any).renderRaw(value, "account-A:g1", ["eye_video"]),
    fixture,
  );
  const record = page.getByRole("switch", {
    name: "Record eye video on this device",
    exact: true,
  });
  await expect(record).not.toBeChecked();
  await expect(record).toBeDisabled();
  await expect(
    page.getByText(
      "Eye video stopped locally. Its exact revocation request or physical cleanup may still be pending.",
      { exact: true },
    ),
  ).toBeVisible();
  await page
    .getByRole("button", { name: "Stop and revoke eye video", exact: true })
    .click();
  await expect
    .poll(() => page.evaluate(() => (window as any).rawEvents))
    .toEqual([{ kind: "revoke", kinds: ["eye_video"] }]);
  await expect(
    page.getByText(fixture.receipt_id, { exact: true }),
  ).toBeVisible();
});

test("actual raw export component keeps every source and separate acknowledgment off until exact purpose review, then resets for another owner", async ({
  page,
}) => {
  await page.evaluate(
    (value) => (window as any).renderRawExport(value),
    rawExport,
  );
  const source = page.getByRole("switch", {
      name: "Export raw eye ROI frames 50000000",
      exact: true,
    }),
    ack = page.getByRole("switch", {
      name: "I reviewed this exact separate raw export purpose and selected sources",
      exact: true,
    });
  await expect(source).not.toBeChecked();
  await expect(ack).not.toBeChecked();
  await expect(ack).toBeDisabled();
  await source.check();
  await expect(ack).toBeDisabled();
  await page
    .getByRole("button", {
      name: "Read complete raw export notice",
      exact: true,
    })
    .click();
  await expect(
    page.getByText(rawExport.scopes[0].export_notice.content, { exact: true }),
  ).toBeVisible();
  await ack.check();
  await expect
    .poll(() =>
      page.evaluate(() => (window as any).rawEvents.at(-1).choice.artifact_ids),
    )
    .toEqual([rawExport.scopes[0].artifacts[0].artifact_id]);
  await page.evaluate(
    (value) => (window as any).renderRawExport(value, "account-B:g2"),
    rawExport,
  );
  await expect(source).not.toBeChecked();
  await expect(ack).not.toBeChecked();
  await expect(ack).toBeDisabled();
});

test("expired or unselected raw export sources remain unavailable while structured export stays separate", async ({
  page,
}) => {
  const value = clone(rawExport);
  value.scopes[0].expires_at = "2026-10-11T11:59:00Z";
  await page.evaluate((value) => (window as any).renderRawExport(value), value);
  await expect(
    page.getByRole("switch", {
      name: "Export raw eye ROI frames 50000000",
      exact: true,
    }),
  ).toBeDisabled();
  await expect(
    page.getByText(
      "Export authorization expired. Structured evidence export remains separate.",
      { exact: true },
    ),
  ).toBeVisible();
  await page.evaluate(
    (value) =>
      (window as any).renderRawExport(value, "account-A:g1", {
        kind: "single",
        session_ids: ["00000000-0000-4000-8000-000000000001"],
      }),
    rawExport,
  );
  await expect(
    page.getByRole("switch", {
      name: "Export raw eye ROI frames 50000000",
      exact: true,
    }),
  ).toBeDisabled();
  expect(await page.evaluate(() => (window as any).rawEvents)).toEqual([]);
});

test("raw upload selection is explicit per file and local-only, expired or revoked recordings cannot join a check upload", async ({
  page,
}) => {
  const file = {
    local_id: "50000000-0000-4000-8000-000000000001",
    study_id: fixture.study_id,
    session_id: rawExport.scopes[0].artifacts[0].session_id,
    attempt_id: "40000000-0000-4000-8000-000000000001",
    artifact_kind: "eye_video",
    format: "OTGD-EYE-ROI-v1",
    media_type: "application/octet-stream",
    sha256: "a".repeat(64),
    size_bytes: 128,
    capture_started_at: "2026-10-11T00:00:01Z",
    consent_record_id: fixture.consent_record_id,
    permission: {
      record: true,
      upload: true,
      receipt_id: fixture.receipt_id,
      policy_id: fixture.policy.policy_id,
      policy_version: fixture.policy.version,
      policy_sha256: fixture.policy.sha256,
      raw_notice_version: fixture.policy.raw_notice.version,
      raw_notice_sha256: fixture.policy.raw_notice.sha256,
    },
    state: "local",
    server_artifact_id: null,
    created_at: "2026-10-11T00:00:10Z",
    retention_due_at: "2026-10-13T00:00:01Z",
    error: null,
  };
  await page.evaluate(
    (value) => (window as any).renderRawUpload([value]),
    file,
  );
  const choice = page.getByRole("switch", {
    name: "Include eye ROI recording 50000000",
    exact: true,
  });
  await expect(choice).not.toBeChecked();
  expect(await page.evaluate(() => (window as any).rawEvents)).toEqual([]);
  await choice.check();
  await expect
    .poll(() => page.evaluate(() => (window as any).rawEvents.at(-1)))
    .toEqual({ kind: "upload_choice", ids: [file.local_id] });
  for (const [index, blocked] of [
    { ...file, permission: { ...file.permission, upload: false } },
    { ...file, retention_due_at: "2026-10-11T00:00:00Z" },
    { ...file, state: "quarantined" },
  ].entries()) {
    await page.evaluate(
      ({ blocked, index }) =>
        (window as any).renderRawUpload([blocked], "blocked-" + index),
      { blocked, index },
    );
    await expect(choice).toBeDisabled();
    await expect(choice).not.toBeChecked();
  }
  await page.evaluate(
    (value) =>
      (window as any).renderRawUpload([value], "fenced", {
        [value.study_id]: ["eye_video"],
      }),
    file,
  );
  await expect(choice).toBeDisabled();
});

test("actual service component labels conditional approved channels and model support, while the fictional build refuses both", async ({
  page,
}) => {
  await page.evaluate(
    () => ((window as any).process = { env: { NODE_ENV: "test" } }),
  );
  await page.addScriptTag({ content: ordinaryAvailability });
  const caps = {
    inference_available: true,
    channels: {
      eyes: { available: true, reason_codes: [] },
      ecg: { available: false, reason_codes: ["NO_QUALIFIED_CONFIGURATION"] },
    },
  };
  await page.evaluate(
    (value) => (window as any).renderAvailability(value),
    caps,
  );
  await expect(
    page.getByText("Approved acquisition available", { exact: true }),
  ).toHaveCount(1);
  await expect(
    page.getByText("Qualified acquisition unavailable", { exact: true }),
  ).toHaveCount(1);
  await expect(
    page.getByText(
      "Conditional on qualified immutable session evidence and current approvals",
      { exact: true },
    ),
  ).toBeVisible();
  await page.evaluate(
    (value) => (window as any).renderAvailability(value, true),
    caps,
  );
  await expect(
    page.getByText(
      "Version 1.1 proof-bound research endpoint support; no model or approval is bundled",
      { exact: true },
    ),
  ).toBeVisible();
  await page.setContent('<main id="root"></main>');
  await page.addScriptTag({ content: hostedAvailability });
  await page.evaluate(
    (value) => (window as any).renderAvailability(value),
    caps,
  );
  await expect(
    page.getByText("Acquisition unavailable in fictional preview", {
      exact: true,
    }),
  ).toHaveCount(2);
  await expect(
    page.getByText("Unavailable in fictional preview", { exact: true }),
  ).toBeVisible();
  await expect(
    page.getByText("Approved acquisition available", { exact: true }),
  ).toHaveCount(0);
});
