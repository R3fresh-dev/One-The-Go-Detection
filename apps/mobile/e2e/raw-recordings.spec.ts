import { test, expect } from "@playwright/test";
import { build, buildSync } from "esbuild";
import { resolve } from "node:path";
import fixture from "../testfixtures/backend-raw-recordings.json";
import privacyReceipt from "../testfixtures/backend-privacy-deletion-receipt.json";
import { clone, digest, digestText } from "../src/core/integrity";
import { readFileSync } from "node:fs";
import researchFixture from "../testfixtures/backend-research-result.json";
import participantFixture from "../testfixtures/backend-participant-acquisition.json";
import capabilitiesFixture from "../testfixtures/backend-capabilities.json";
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
const participantBundle = buildSync({
  entryPoints: [resolve("e2e/fixtures/participant-component.tsx")],
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
    "process.env.EXPO_PUBLIC_HOSTED_PREVIEW": '"false"',
  },
  loader: { ".tsx": "tsx" },
}).outputFiles![0]!.text;
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

function screenOptions(entry: string, native = false) {
  return {
    entryPoints: [resolve(`e2e/fixtures/${entry}.tsx`)],
    bundle: true,
    write: false,
    platform: "browser" as const,
    format: "iife" as const,
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
    alias: {
      "react-native": resolve(
        `e2e/fixtures/${native ? "permissions-native-shim.ts" : "native-web-shim.js"}`,
      ),
      ...(native
        ? {
            "expo-camera": resolve("e2e/fixtures/permission-adapters.ts"),
            "expo-local-authentication": resolve(
              "e2e/fixtures/permission-adapters.ts",
            ),
            "expo-clipboard": resolve("e2e/fixtures/permission-adapters.ts"),
          }
        : {}),
    },
    define: {
      "process.env.NODE_ENV": '"test"',
      "process.env.EXPO_PUBLIC_APP_ENV": '"local"',
      "process.env.EXPO_PUBLIC_HOSTED_PREVIEW": '"false"',
    },
  };
}
const alcoholBundle = buildSync(screenOptions("alcohol-component"))
  .outputFiles![0]!.text;
const receiptBundle = buildSync(screenOptions("privacy-raw-receipt-component"))
  .outputFiles![0]!.text;
let permissionsBundle: string;
test.beforeAll(async () => {
  permissionsBundle = (
    await build({
      ...screenOptions("permissions-component", true),
      plugins: [
        {
          name: "controlled-permission-boundary",
          setup(builder) {
            builder.onResolve({ filter: /modules\/device-transport$/ }, () => ({
              path: resolve("e2e/fixtures/permission-adapters.ts"),
            }));
          },
        },
      ],
    })
  ).outputFiles![0]!.text;
});

const screenErrors = new WeakMap<object, string[]>();
async function screenDOM(page: any, content: string) {
  const errors: string[] = [];
  screenErrors.set(page, errors);
  page.on("pageerror", (error: Error) => errors.push(error.message));
  await page.setContent('<main id="root"></main>');
  await page.addScriptTag({ content });
}
test.afterEach(async ({ page }) => {
  expect(screenErrors.get(page) ?? []).toEqual([]);
});

test("alcohol copy remains accurate for measurement, guest and admitted research contexts", async ({
  page,
}) => {
  await screenDOM(page, alcoholBundle);
  for (const kind of ["measurement", "guest_demo", "research"]) {
    const check = clone(researchFixture.check) as any;
    if (kind !== "research") {
      check.kind = kind;
      check.result = null;
    }
    await page.evaluate((value) => (window as any).renderAlcohol(value), check);
    await expect(
      page.getByText("Qualified capture unavailable", { exact: true }),
    ).toBeVisible();
    await expect(
      page.getByText("mg/L breath alcohol", { exact: true }),
    ).toBeVisible();
    await expect(
      page.getByText(
        "No automatic combined classification; research co-use requires model-specific authority",
        { exact: true },
      ),
    ).toBeVisible();
    await expect(
      page.getByText("No classification exists", { exact: true }),
    ).toHaveCount(0);
    await expect(
      page.getByText("Driving threshold or clearance", { exact: true }),
    ).toBeVisible();
    await expect(page.getByText("Unavailable", { exact: true })).toHaveCount(2);
  }
});

test("alcohol qualifiers retain zero, low, censored, invalid and simulated evidence without clearance from history through result and detail", async ({
  page,
}) => {
  await screenDOM(page, alcoholBundle);
  for (const variant of [
    {
      qualifier: "quantified",
      source: "prototype_sensor",
      value: 0,
      text: "0.000",
    },
    {
      qualifier: "quantified",
      source: "prototype_sensor",
      value: 0.001,
      text: "0.001",
    },
    {
      qualifier: "below_loq",
      source: "prototype_sensor",
      value: null,
      text: "—",
    },
    {
      qualifier: "not_detected",
      source: "prototype_sensor",
      value: null,
      text: "—",
    },
    {
      qualifier: "invalid",
      source: "prototype_sensor",
      value: null,
      text: "—",
    },
    {
      qualifier: "quantified",
      source: "simulated",
      value: 0.001,
      text: "0.001",
    },
  ]) {
    const check = clone(researchFixture.check) as any;
    check.alcohol = {
      ...check.alcohol,
      qualifier: variant.qualifier,
      source: variant.source,
      value_mg_l: variant.value,
      measured_at: "2026-10-11T07:08:09Z",
      // Hypothetical reporting boundary only; no qualified instrument exists.
      limits: { lod_mg_l: 0, loq_mg_l: 0, upper_mg_l: 1 },
    };
    await page.evaluate(
      (value) => (window as any).renderAlcohol(value, "history"),
      check,
    );
    await expect(
      page.getByText("Your check history", { exact: true }),
    ).toBeVisible();
    await expect(
      page.getByText(
        /safe to drive|cleared to drive|legally cleared|combined score/i,
      ),
    ).toHaveCount(0);
    await page
      .getByRole("button", { name: /Historical research result/ })
      .click();
    await expect(page.getByText("83.2%", { exact: true })).toBeVisible();
    await expect(
      page.getByText("above threshold", { exact: true }),
    ).toBeVisible();
    const card = page
      .getByText("Separate alcohol measurement", { exact: true })
      .locator("..");
    await expect(
      card.getByText(`${variant.text} mg/L`, { exact: true }),
    ).toBeVisible();
    await expect(card.getByText("mg/L", { exact: true })).toBeVisible();
    await expect(
      card.getByText(
        `${variant.qualifier.replaceAll("_", " ")} / ${variant.source.replaceAll("_", " ")}`,
        { exact: true },
      ),
    ).toBeVisible();
    await expect(
      card.getByText("2026-10-11T07:08:09Z", { exact: true }),
    ).toBeVisible();
    await expect(
      card.getByText(
        "No BAC conversion or cannabis impairment adjustment is calculated.",
        { exact: true },
      ),
    ).toBeVisible();
    await expect(
      page.getByText(
        /safe to drive|cleared to drive|legally cleared|combined score/i,
      ),
    ).toHaveCount(0);
    await page.getByRole("button", { name: /About this result/ }).click();
    await expect(
      page.getByText("Evidence & context", { exact: true }),
    ).toBeVisible();
    await expect(
      page.getByText(
        /safe to drive|cleared to drive|legally cleared|combined score/i,
      ),
    ).toHaveCount(0);
  }
});

test("Settings reads denied, restricted, undetermined and failed camera status without prompting and opens OS settings only explicitly", async ({
  page,
}) => {
  await screenDOM(page, permissionsBundle);
  for (const value of [
    {
      exact: "denied",
      status: "denied",
      canAskAgain: true,
      label: "Denied · request only in eye preview",
    },
    {
      exact: "denied",
      status: "denied",
      canAskAgain: false,
      label: "Denied · review app settings",
    },
    {
      exact: "restricted",
      status: "denied",
      canAskAgain: false,
      label: "Restricted by device policy",
    },
    {
      exact: "not_requested",
      status: "undetermined",
      canAskAgain: true,
      label: "Not requested",
    },
    {
      exact: "unknown",
      status: "denied",
      canAskAgain: false,
      fail: true,
      label: "Status unavailable · refresh to retry",
    },
  ]) {
    await page.evaluate((value) => {
      const c = (window as any).permissionControl;
      c.exact = value.exact;
      c.fail = !!value.fail;
      c.permission = {
        status: value.status,
        canAskAgain: value.canAskAgain,
        granted: false,
        expires: "never",
      };
      (window as any).renderPermissions(value.label);
    }, value);
    const camera = page
      .getByText("Camera · eye-positioning preview", { exact: true })
      .locator("..");
    // Refresh also covers retained Settings instances before the account-boundary repair.
    await page
      .getByRole("button", { name: "Refresh permission status", exact: true })
      .click();
    await expect(camera.getByText(value.label, { exact: true })).toBeVisible();
    await page.evaluate(() => (window as any).permissionActive());
    await expect(camera.getByText(value.label, { exact: true })).toBeVisible();
    expect(
      await page.evaluate(() => (window as any).permissionControl.prompts),
    ).toBe(0);
  }
  expect(
    await page.evaluate(() => (window as any).permissionControl.settings),
  ).toBe(0);
  await page
    .getByRole("button", { name: "Open device settings", exact: true })
    .click();
  expect(
    await page.evaluate(() => (window as any).permissionControl.settings),
  ).toBe(1);
  await page.evaluate(() => {
    const c = (window as any).permissionControl;
    c.fail = false;
    c.exact = "granted";
    c.permission = {
      status: "granted",
      granted: true,
      canAskAgain: true,
      expires: "never",
    };
    (window as any).permissionActive();
  });
  await expect(
    page
      .getByText("Camera · eye-positioning preview", { exact: true })
      .locator("..")
      .getByText("Granted", { exact: true }),
  ).toBeVisible();
  expect(
    await page.evaluate(() => (window as any).permissionControl.prompts),
  ).toBe(0);
});

test("Settings ignores out-of-order and unmounted camera reads and replaces stale account and generation observations", async ({
  page,
}) => {
  await screenDOM(page, permissionsBundle);
  await page.evaluate(() => {
    (window as any).permissionControl.defer = true;
    (window as any).renderPermissions();
  });
  const camera = page
    .getByText("Camera · eye-positioning preview", { exact: true })
    .locator("..");
  await expect
    .poll(() =>
      page.evaluate(() => (window as any).permissionControl.pending.length),
    )
    .toBe(1);
  await page
    .getByRole("button", { name: "Refresh permission status", exact: true })
    .click();
  await page.evaluate(() => {
    const c = (window as any).permissionControl;
    c.pending[1].resolve({
      status: "granted",
      granted: true,
      canAskAgain: true,
      expires: "never",
    });
  });
  await expect(camera.getByText("Granted", { exact: true })).toBeVisible();
  await page.evaluate(() =>
    (window as any).permissionControl.pending[0].resolve({
      status: "denied",
      granted: false,
      canAskAgain: false,
      expires: "never",
    }),
  );
  await expect(camera.getByText("Granted", { exact: true })).toBeVisible();
  // A controller can invalidate its epoch before React commits navigation.
  // That interval must not let the old card publish its outstanding OS read.
  await page
    .getByRole("button", { name: "Refresh permission status", exact: true })
    .click();
  await page.evaluate(() => {
    (window as any).changePermissionEpoch("fictional-between-render");
    (window as any).permissionControl.pending.at(-1).resolve({
      status: "denied",
      granted: false,
      canAskAgain: false,
      expires: "never",
    });
  });
  await page.clock.runFor(50);
  await expect(camera.getByText("Granted", { exact: true })).toBeVisible();
  for (const [epoch, generation] of [
    ["fictional-account-B:g1", 1],
    ["fictional-account-B:g1", 2],
  ] as const) {
    await page
      .getByRole("button", { name: "Refresh permission status", exact: true })
      .click();
    const old = await page.evaluate(
      () => (window as any).permissionControl.pending.length - 1,
    );
    await page.evaluate(
      ({ epoch, generation }) =>
        (window as any).renderPermissions(epoch, generation),
      { epoch, generation },
    );
    await page.evaluate(
      (index) =>
        (window as any).permissionControl.pending[index].resolve({
          status: "denied",
          granted: false,
          canAskAgain: false,
          expires: "never",
        }),
      old,
    );
    await expect(
      camera.getByText("Not checked", { exact: true }),
    ).toBeVisible();
    await expect
      .poll(() =>
        page.evaluate(() => (window as any).permissionControl.pending.length),
      )
      .toBe(old + 2);
    await page.evaluate(
      (index) =>
        (window as any).permissionControl.pending[index + 1].resolve({
          status: "granted",
          granted: true,
          canAskAgain: true,
          expires: "never",
        }),
      old,
    );
    await expect(camera.getByText("Granted", { exact: true })).toBeVisible();
  }
  await page
    .getByRole("button", { name: "Refresh permission status", exact: true })
    .click();
  await page.evaluate(() => (window as any).unmountPermissions());
  await expect(
    page.getByText("Device permissions", { exact: true }),
  ).toHaveCount(0);
  await page.evaluate(() => {
    const c = (window as any).permissionControl;
    c.pending.at(-1).resolve({
      status: "denied",
      granted: false,
      canAskAgain: false,
      expires: "never",
    });
  });
  await expect(
    page.getByText("Denied · review app settings", { exact: true }),
  ).toHaveCount(0);
  expect(
    await page.evaluate(() => ({
      prompts: (window as any).permissionControl.prompts,
      listeners: (window as any).permissionControl.listeners.size,
    })),
  ).toEqual({ prompts: 0, listeners: 0 });
});

test.beforeEach(async ({ page }) => {
  await page.clock.install({ time: Date.parse("2026-10-11T12:00:00Z") });
  await page.goto("/");
  await page.setContent('<html><body><main id="root"></main></body></html>');
  await page.addScriptTag({ content: bundle });
});
test("eye and ECG descriptions follow the approved observation and actual provenance without claiming measured light onset", async ({
  page,
}) => {
  await page.setContent('<html><body><main id="root"></main></body></html>');
  await page.addScriptTag({ content: participantBundle });
  const check = clone(researchFixture.check) as any,
    caps = clone(capabilitiesFixture) as any;
  check.snapshot.eyes = {
    ...check.snapshot.eyes,
    status: "not_collected",
    baseline_diameter_mm: null,
    scale_basis: "normalized",
  };
  check.snapshot.cardiac = {
    ...check.snapshot.cardiac,
    modality: "ecg",
    source: "prototype_sensor",
    ecg_rmssd_ms: null,
  };
  const config = {
    study_id: check.snapshot.study_id,
    protocol_id: check.snapshot.protocol_id,
    configuration_id: "fictional-reviewed-optics",
    configuration_version: "v1",
    configuration_hash: "a".repeat(64),
    submitted_sha256: "b".repeat(64),
    expires_at: "2026-10-12T00:00:00Z",
    supported_phone_models: ["fictional-phone"],
    software_adapter_id: "optical_roi_v1",
  };
  check.context.configuration_refs = [
    {
      id: config.configuration_id,
      version: "v1",
      sha256: config.configuration_hash,
      scope: "measurement_collection",
    },
  ];
  caps.channels.eyes = {
    available: true,
    software_available: true,
    authorization_available: true,
    reason_codes: [],
    configurations: [config],
  };
  await page.evaluate(
    ({ check, caps }) => (window as any).renderParticipantCopy(check, caps),
    { check, caps },
  );
  await expect(
    page.getByText(/Approved optical ROI acquisition is available/),
  ).toBeVisible();
  await expect(
    page.getByText(
      "Physical illumination onset unmeasured · response magnitude and latency withheld",
      { exact: true },
    ),
  ).toBeVisible();
  await expect(
    page.getByText("Not measured by this ECG acquisition", { exact: true }),
  ).toBeVisible();
  await expect(
    page.getByText("Fictional ECG example", { exact: true }),
  ).toHaveCount(0);
  check.snapshot.eyes = {
    ...check.snapshot.eyes,
    status: "valid",
    source: "prototype_sensor",
    baseline_diameter_mm: 4,
    scale_basis: "calibrated_mm",
  };
  check.snapshot.cardiac.ecg_rmssd_ms = 20;
  await page.evaluate(
    ({ check, caps }) => (window as any).renderParticipantCopy(check, caps),
    { check, caps },
  );
  await expect(
    page.getByText(
      /retains a diameter scale from the approved geometry calibration/,
    ),
  ).toBeVisible();
  await expect(
    page.getByText(
      "Device-reported ECG interval feature; no diagnostic interpretation",
      { exact: true },
    ),
  ).toBeVisible();
  check.kind = "guest_demo";
  check.snapshot.cardiac.source = "simulated";
  check.snapshot.eyes.source = "simulated";
  await page.evaluate(
    ({ check, caps }) => (window as any).renderParticipantCopy(check, caps),
    { check, caps },
  );
  await expect(
    page.getByText(/Fictional eye values are examples/),
  ).toBeVisible();
  await expect(
    page.getByText("Fictional ECG example", { exact: true }),
  ).toBeVisible();
  await expect(
    page.getByText("Approved optical acquisition unavailable for this check", {
      exact: true,
    }),
  ).toBeVisible();
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

const participantConfig = () =>
  clone(
    participantFixture.import_flow.capabilities.channels.saliva
      .configurations[0],
  ) as any;
function cardiacPreparation(scope = "engineering_bench") {
  const configuration = participantConfig(),
    text =
      "Fictional cardiac setup instructions for the browser software test.";
  configuration.participant_protocol = {
    schema_version: "1.0.0",
    instruction_id: "fictional-cardiac-preparation",
    version: "v1",
    text,
    sha256: digestText(text),
    required_confirmations: [
      "rest_completed",
      "posture_confirmed",
      "activity_confirmed",
      "contact_confirmed",
      "isolation_confirmed",
    ].map((id) => ({ id, text: id })),
    maximum_acknowledgment_age_seconds: 120,
    kind: "cardiac",
    operating_scope: scope,
    operating_state_verifier: "participant_declaration_only",
    rest_duration_seconds: 30,
    posture_instruction: "Sit in the declared posture",
    activity_instruction: "Remain still during the rest",
    contact_instruction: "Use only the declared bench contacts",
    isolation_instruction: "No human leads; this is a software test",
    permitted_setups: [
      {
        id: "fictional-bench",
        description: "Fictional portable bench",
        power_state: "battery",
        charging_state: "off",
        cable_state: "none",
        contact_or_lead_configuration: "bench contacts",
      },
    ],
  };
  configuration.participant_protocol_sha256 = digest(
    configuration.participant_protocol,
  );
  return configuration;
}
async function participantDOM(page: any) {
  await page.setContent('<html><body><main id="root"></main></body></html>');
  await page.addScriptTag({ content: participantBundle });
}
test("approved rest begins after online preparation, uses monotonic time, and needs exact unchecked declarations before capture", async ({
  page,
}) => {
  await participantDOM(page);
  const configuration = cardiacPreparation();
  await page.evaluate(
    (value) => (window as any).renderPreparation(value),
    configuration,
  );
  const start = page.getByRole("button", {
    name: "Start authorized pulse capture",
    exact: true,
  });
  await expect(start).toBeDisabled();
  for (const declaration of configuration.participant_protocol
    .required_confirmations)
    await expect(
      page.getByRole("switch", { name: declaration.text, exact: true }),
    ).not.toBeChecked();
  await page
    .getByRole("radio", { name: "Fictional portable bench", exact: true })
    .click();
  await page
    .getByRole("button", { name: "Start approved rest period", exact: true })
    .click();
  await page.clock.fastForward(60000);
  await expect(
    page.getByText(/Begin only after the service saves/),
  ).toBeVisible();
  await expect(start).toBeDisabled();
  await page.evaluate(() => (window as any).resolvePreparation());
  await expect(
    page.getByText("Required foreground rest: 30 seconds remaining.", {
      exact: true,
    }),
  ).toBeVisible();
  await expect(start).toBeDisabled();
  await expect(
    page.getByRole("switch", { name: "rest_completed", exact: true }),
  ).toBeDisabled();
  await page.clock.fastForward(30000);
  for (const declaration of configuration.participant_protocol
    .required_confirmations)
    await page
      .getByRole("switch", { name: declaration.text, exact: true })
      .click();
  await expect(start).toBeEnabled();
  await start.click();
  const calls = await page.evaluate(() => (window as any).participantCalls);
  expect(calls.map((call: any) => call.kind)).toEqual(["prepare", "capture"]);
  expect(calls[1].input.participant_protocol_sha256).toBe(
    configuration.participant_protocol_sha256,
  );
  expect(calls[1].input.confirmations.sort()).toEqual(
    configuration.participant_protocol.required_confirmations
      .map((item: any) => item.id)
      .sort(),
  );
  expect(calls[1].raw).toBe(false);
  await expect(start).toBeDisabled();
});
test("interruption and a changed instruction envelope discard rest and checks; participant declarations cannot enable human ECG", async ({
  page,
}) => {
  await participantDOM(page);
  const configuration = cardiacPreparation();
  await page.evaluate(
    (value) => (window as any).renderPreparation(value),
    configuration,
  );
  await page
    .getByRole("radio", { name: "Fictional portable bench", exact: true })
    .click();
  await page
    .getByRole("button", { name: "Start approved rest period", exact: true })
    .click();
  await page.evaluate(() => {
    Object.defineProperty(document, "visibilityState", {
      configurable: true,
      value: "hidden",
    });
    document.dispatchEvent(new Event("visibilitychange"));
    (window as any).resolvePreparation();
  });
  await expect(
    page.getByText(/Begin only after the service saves/),
  ).toBeVisible();
  const calls = await page.evaluate(() => (window as any).participantCalls);
  expect(calls.map((call: any) => call.kind)).toEqual(["prepare", "stop"]);
  const changed = cardiacPreparation("human_participant");
  changed.submitted_sha256 = "f".repeat(64);
  await page.evaluate(
    (value) => (window as any).renderPreparation(value, "ecg"),
    changed,
  );
  await expect(
    page.getByText(/Human ECG acquisition is unavailable/),
  ).toBeVisible();
  await expect(
    page.getByRole("button", {
      name: "Start approved rest period",
      exact: true,
    }),
  ).toBeDisabled();
  await expect(
    page.getByRole("button", {
      name: "Start authorized ecg capture",
      exact: true,
    }),
  ).toBeDisabled();
  await expect(
    page.getByRole("switch", { name: "isolation_confirmed", exact: true }),
  ).not.toBeChecked();
});
test("a monotonic regression resets approved rest and declarations until an explicit new preparation", async ({
  page,
}) => {
  await participantDOM(page);
  const configuration = cardiacPreparation();
  await page.evaluate((value) => {
    (window as any).restTick = 1000;
    const wallAnchor = Date.now();
    Object.defineProperty(Date, "now", {
      configurable: true,
      value: () => wallAnchor + (window as any).restTick - 1000,
    });
    Object.defineProperty(performance, "now", {
      configurable: true,
      value: () => (window as any).restTick,
    });
    (window as any).renderPreparation(value);
  }, configuration);
  await page
    .getByRole("radio", { name: "Fictional portable bench", exact: true })
    .click();
  await page
    .getByRole("button", { name: "Start approved rest period", exact: true })
    .click();
  await page.evaluate(() => (window as any).resolvePreparation());
  await expect(
    page.getByText("Required foreground rest: 30 seconds remaining.", {
      exact: true,
    }),
  ).toBeVisible();
  await page.evaluate(() => {
    (window as any).restTick = 5000;
  });
  await page.clock.fastForward(200);
  await expect(
    page.getByText("Required foreground rest: 26 seconds remaining.", {
      exact: true,
    }),
  ).toBeVisible();
  await page
    .getByRole("switch", { name: "posture_confirmed", exact: true })
    .click();
  await page.evaluate(() => {
    (window as any).restTick = 3000;
  });
  await page.clock.fastForward(200);
  await expect(page.getByText(/Preparation timing changed/)).toBeVisible();
  await expect(
    page.getByRole("switch", { name: "posture_confirmed", exact: true }),
  ).not.toBeChecked();
  await page.evaluate(() => {
    (window as any).restTick = 100000;
  });
  await page.clock.fastForward(200);
  await expect(
    page.getByRole("button", {
      name: "Start authorized pulse capture",
      exact: true,
    }),
  ).toBeDisabled();
  expect(
    (await page.evaluate(() => (window as any).participantCalls)).map(
      (c: any) => c.kind,
    ),
  ).toEqual(["prepare", "stop"]);
});
test("unmount and a replacement approval envelope stop pending preparation and cannot apply its late receipt", async ({
  page,
}) => {
  await participantDOM(page);
  const configuration = cardiacPreparation();
  await page.evaluate(
    (value) => (window as any).renderPreparation(value),
    configuration,
  );
  await page
    .getByRole("radio", { name: "Fictional portable bench", exact: true })
    .click();
  await page
    .getByRole("button", { name: "Start approved rest period", exact: true })
    .click();
  await page.evaluate(() => {
    (window as any).oldPreparation = (window as any).resolvePreparation;
    (window as any).unmountParticipant();
  });
  await expect(
    page.getByRole("button", {
      name: "Start approved rest period",
      exact: true,
    }),
  ).toHaveCount(0);
  const changed = { ...configuration, submitted_sha256: "f".repeat(64) };
  await page.evaluate((value) => {
    (window as any).renderPreparation(value);
    (window as any).oldPreparation();
  }, changed);
  await expect(
    page.getByText(/Begin only after the service saves/),
  ).toBeVisible();
  await expect(
    page.getByRole("button", {
      name: "Start authorized pulse capture",
      exact: true,
    }),
  ).toBeDisabled();
  await expect(
    page.getByRole("switch", { name: "posture_confirmed", exact: true }),
  ).not.toBeChecked();
  expect(
    (await page.evaluate(() => (window as any).participantCalls)).map(
      (c: any) => c.kind,
    ),
  ).toEqual(["prepare", "stop"]);
});
test("laboratory method review pins the actual selected method without BLE and resets acknowledgement on document replacement", async ({
  page,
}) => {
  await participantDOM(page);
  const configuration = participantConfig(),
    method = configuration.participant_protocol.methods[0];
  await page.evaluate(
    (value) => (window as any).renderLabMethod(value),
    configuration,
  );
  const start = page.getByRole("button", {
    name: "Acknowledge method and start specimen draft",
    exact: true,
  });
  await expect(start).toBeDisabled();
  await expect(page.getByText(/does not use a Bluetooth reader/)).toBeVisible();
  await page
    .getByRole("radio", {
      name: `${method.id} · ${method.version}`,
      exact: true,
    })
    .click();
  await expect(
    page.getByText(method.instructions, { exact: true }),
  ).toBeVisible();
  await page
    .getByRole("switch", {
      name: configuration.participant_protocol.required_confirmations[0].text,
      exact: true,
    })
    .click();
  await start.click();
  const calls = await page.evaluate(() => (window as any).participantCalls);
  expect(calls[0].input.collection_method_id).toBe(method.id);
  expect(calls[0].input.collection_method_version).toBe(method.version);
  expect(calls[0].input.setup_id).toBeNull();
  const changed = clone(configuration);
  changed.submitted_sha256 = "e".repeat(64);
  changed.participant_protocol.version = "v2";
  changed.participant_protocol_sha256 = digest(changed.participant_protocol);
  await page.evaluate(
    (value) => (window as any).renderLabMethod(value),
    changed,
  );
  await expect(start).toBeDisabled();
  await expect(
    page.getByRole("switch", {
      name: changed.participant_protocol.required_confirmations[0].text,
      exact: true,
    }),
  ).not.toBeChecked();
});
test("specimen form records actual quantities, explicit unknowns and handling while offering no participant concentration entry", async ({
  page,
}) => {
  await participantDOM(page);
  const configuration = participantConfig(),
    request = clone(participantFixture.import_flow.collection_request);
  await page.evaluate(
    ({ configuration, request }) =>
      (window as any).renderSpecimenForm(configuration, request),
    { configuration, request },
  );
  await expect(
    page.getByRole("textbox", { name: /concentration/i }),
  ).toHaveCount(0);
  await expect(
    page.getByRole("textbox", {
      name: "Observed saliva volume (mL)",
      exact: true,
    }),
  ).toHaveValue("");
  await page
    .getByRole("button", {
      name: "Record actual collection time now",
      exact: true,
    })
    .click();
  await page
    .getByRole("radio", {
      name: "Adequate according to the approved method",
      exact: true,
    })
    .click();
  for (const [label, value] of [
    ["Observed saliva volume (mL)", "1"],
    ["Observed buffer volume (mL)", "1"],
    ["Recorded dilution factor", "2"],
    ["collector lot", "FICTIONAL-LOT"],
    ["container id", "FICTIONAL-CONTAINER"],
    ["cartridge lot", "FICTIONAL-CARTRIDGE"],
    ["cartridge expiry", "2026-10-12T12:00:00Z"],
  ] as const)
    await page.getByRole("textbox", { name: label, exact: true }).fill(value);
  await page
    .getByText("Reason for unknown collector id", { exact: true })
    .locator("..")
    .getByRole("radio", { name: "unknown", exact: true })
    .click();
  await page
    .getByRole("button", { name: "Record sealed now", exact: true })
    .click();
  await page
    .getByRole("button", {
      name: "Submit exact specimen declaration",
      exact: true,
    })
    .click();
  const calls = await page.evaluate(() => (window as any).participantCalls);
  expect(calls).toHaveLength(1);
  expect(calls[0].body.saliva_volume_ml).toBe(1);
  expect(calls[0].body.buffer_volume_ml).toBe(1);
  expect(calls[0].body.dilution_factor).toBe(2);
  expect(calls[0].body.collector_id).toBeNull();
  expect(calls[0].body.missing_reasons).toEqual({ collector_id: "unknown" });
  expect(calls[0].body.storage_handling_events[0].event).toBe("sealed");
  expect(Object.keys(calls[0].body)).not.toContain("concentration");
  const draft = await page.evaluate(() => (window as any).lastSpecimenDraft);
  expect(draft.saliva_volume_ml).toBe("1");
});

test("pending laboratory UI preserves the draft, refreshes actual admitted analysis and requires explicit cancellation without inventing chemistry", async ({
  page,
}) => {
  await participantDOM(page);
  const configuration = participantConfig(),
    flow = participantFixture.import_flow;
  await page.evaluate(
    ({ configuration, flow }) =>
      (window as any).renderLabLifecycle(configuration, flow),
    { configuration, flow },
  );
  await expect(
    page.getByText(
      /Laboratory analysis pending\. This owned cloud check remains a draft/,
    ),
  ).toBeVisible();
  await expect(
    page.getByRole("textbox", { name: /concentration/i }),
  ).toHaveCount(0);
  await page
    .getByRole("button", {
      name: "Save pending draft and resume later",
      exact: true,
    })
    .click();
  expect(await page.evaluate(() => (window as any).participantCalls)).toEqual([
    { kind: "save", state: "pending_lab", frozen: false },
  ]);
  await page
    .getByRole("button", {
      name: "Refresh independent laboratory analysis",
      exact: true,
    })
    .click();
  await expect(
    page.getByText(/Independent laboratory analysis received/),
  ).toBeVisible();
  expect(
    (await page.evaluate(() => (window as any).participantCalls))[1],
  ).toEqual({ kind: "refresh", sample: flow.collection_request.sample_id });
  await page.evaluate(
    ({ configuration, flow }) =>
      (window as any).renderLabLifecycle(configuration, flow),
    { configuration, flow },
  );
  await page
    .getByRole("button", {
      name: "End pending laboratory analysis",
      exact: true,
    })
    .click();
  await expect(
    page.getByText(
      /Laboratory analysis pending\. This owned cloud check remains a draft/,
    ),
  ).toBeVisible();
  await page.evaluate(() => (window as any).confirmLaboratoryEnd());
  await expect(
    page.getByText(/The pending analysis ended explicitly/),
  ).toBeVisible();
  await expect(
    page.getByRole("button", {
      name: "Acknowledge method and start specimen draft",
      exact: true,
    }),
  ).toHaveCount(0);
  await expect(
    page.getByText(flow.collection_request.sample_id, { exact: true }),
  ).toBeVisible();
});
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

test("actual raw receipt screen keeps quarantine and cleanup confirmation distinct from retention expiry", async ({
  page,
}) => {
  await screenDOM(page, receiptBundle);
  await page.evaluate(
    (value) => (window as any).renderReceipt("raw", value),
    fixture,
  );
  await expect(
    page.getByText("Eye video · quarantine · retained", { exact: true }),
  ).toBeVisible();
  await expect(
    page.getByText("Retention deadline", { exact: true }),
  ).toBeVisible();
  await expect(page.getByText("Not confirmed", { exact: true })).toBeVisible();
  const changed: any = clone(fixture);
  changed.artifacts[0].state = "cleanup_pending";
  changed.artifacts[0].upload_state = "cleanup_pending";
  changed.artifacts[0].retention_due_at = "2026-10-10T00:00:00.000Z";
  changed.revocations = [
    {
      receipt_id: "70000000-0000-4000-8000-000000000001",
      artifact_kinds: ["eye_video"],
      accepted_at: "2026-10-11T01:00:00Z",
      state: "cleanup_pending",
    },
  ];
  await page.evaluate(
    (value) => (window as any).renderReceipt("raw", value),
    changed,
  );
  await expect(
    page.getByText("Eye video · cleanup pending · cleanup pending", {
      exact: true,
    }),
  ).toBeVisible();
  await expect(
    page.getByText("Eye video · quarantine · retained", { exact: true }),
  ).toHaveCount(0);
  await expect(page.getByText("Not confirmed", { exact: true })).toBeVisible();
  await expect(
    page.getByText("Eye video · cleanup pending", { exact: true }),
  ).toBeVisible();
  await expect(page.getByText(/Oct 10, 2026/)).toBeVisible();
  changed.artifacts[0].state = "purged";
  changed.artifacts[0].upload_state = "purged";
  changed.artifacts[0].cleanup_completed_at = "2026-10-11T02:03:00Z";
  changed.revocations[0].state = "completed";
  await page.evaluate(
    (value) => (window as any).renderReceipt("raw", value),
    changed,
  );
  await expect(
    page.getByText("Eye video · purged · purged", { exact: true }),
  ).toBeVisible();
  await expect(page.getByText("Not confirmed", { exact: true })).toHaveCount(0);
  await expect(page.getByText(/Oct 11, 2026, 02:03/)).toBeVisible();
  await expect(page.getByText(/Oct 10, 2026/)).toBeVisible();
});

test("actual API privacy receipt renders category policy reason and supplied or absent expiry without generic legacy names", async ({
  page,
}) => {
  await screenDOM(page, receiptBundle);
  await page.evaluate(
    (value) => (window as any).renderReceipt("privacy", value),
    privacyReceipt,
  );
  for (const category of privacyReceipt.retained_categories) {
    await expect(
      page.getByText(category.category, { exact: true }),
    ).toBeVisible();
    await expect(
      page.getByText(category.reason, { exact: true }),
    ).toBeVisible();
  }
  await expect(
    page.getByText("No scheduled expiry supplied", { exact: true }),
  ).toHaveCount(6);
  await expect(
    page.getByText("Retention policy basis", { exact: true }),
  ).toHaveCount(6);
  const supplied: any = clone(privacyReceipt);
  supplied.retained_categories[0].expires_at = "2027-02-28T23:59:59.123Z";
  await page.evaluate(
    (value) => (window as any).renderReceipt("privacy", value),
    supplied,
  );
  await expect(
    page.getByText("2027-02-28T23:59:59.123Z", { exact: true }),
  ).toBeVisible();
  const legacy: any = {
    ...privacyReceipt,
    retained_categories: privacyReceipt.retained_categories.map(
      (entry) => entry.category,
    ),
  };
  await page.evaluate(
    (value) => (window as any).renderReceipt("privacy", value),
    legacy,
  );
  for (const category of legacy.retained_categories)
    await expect(page.getByText(category, { exact: true })).toBeVisible();
  await expect(
    page.getByText(
      "Legacy receipt: policy basis, retention reason and expiry were not supplied.",
      { exact: true },
    ),
  ).toHaveCount(6);
  await expect(
    page.getByText("2027-02-28T23:59:59.123Z", { exact: true }),
  ).toHaveCount(0);
});
