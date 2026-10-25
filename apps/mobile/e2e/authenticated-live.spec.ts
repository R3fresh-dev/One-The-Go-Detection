import { test, expect, type Page } from "@playwright/test";
import { createHash, randomUUID } from "node:crypto";
import { constants } from "node:fs";
import { open, readFile, writeFile } from "node:fs/promises";
import { unzipSync } from "fflate";

const API = "http://localhost:8000",
  ISSUER = "http://localhost:8081";
const manifestPath =
  process.env.OTGD_BROWSER_FIXTURE ?? "/tmp/otgd-browser-fixture.json";
const SCOPE =
  "FICTIONAL SOFTWARE BROWSER ACCEPTANCE ONLY; NO HUMAN OR SCIENTIFIC AUTHORITY";
interface Ledger {
  schema_version: number;
  scope: string;
  namespace: string;
  api_origin: string;
  identity_origin: string;
  web_origin: string;
  accounts: Record<string, { session_ids: string[] }>;
  profile_versions?: Record<string, string[]>;
  governed?: Record<
    string,
    {
      study_id: string;
      protocol_id: string;
      invitation_id: string;
      document_version: string;
      document_sha256: string;
    }
  >;
}
async function readLedger(): Promise<Ledger> {
  const handle = await open(
    manifestPath,
    constants.O_RDONLY | constants.O_NOFOLLOW,
  );
  try {
    const stat = await handle.stat();
    expect(
      stat.isFile() &&
        stat.size <= 65_536 &&
        stat.nlink === 1 &&
        (stat.mode & 0o077) === 0,
      "Prepare a private bounded browser fixture ledger before live acceptance",
    ).toBe(true);
    const ledger = JSON.parse(await handle.readFile("utf8")) as Ledger;
    expect(ledger.schema_version).toBe(1);
    expect(ledger.scope).toBe(SCOPE);
    expect(ledger.namespace).toMatch(/^fictional-browser-[a-f0-9]{32}$/);
    expect([
      ledger.api_origin,
      ledger.identity_origin,
      ledger.web_origin,
    ]).toEqual([API, ISSUER, "http://localhost:8082"]);
    expect(Object.keys(ledger.accounts).sort()).toEqual([
      "browser_desktop",
      "browser_mobile",
    ]);
    return ledger;
  } finally {
    await handle.close();
  }
}
async function rememberSession(account: string, id: string, profile = false) {
  expect(id).toMatch(/^[a-f0-9-]{36}$/);
  const ledger = await readLedger();
  const ids = profile
    ? ((ledger.profile_versions ??= {})[account] ??= [])
    : ledger.accounts[account]!.session_ids;
  if (ids.includes(id)) return;
  expect(ids.length).toBeLessThan(500);
  ids.push(id);
  const handle = await open(
    manifestPath,
    constants.O_WRONLY | constants.O_NOFOLLOW,
  );
  try {
    const stat = await handle.stat();
    expect(stat.isFile() && stat.nlink === 1 && (stat.mode & 0o077) === 0).toBe(
      true,
    );
    await handle.truncate();
    await handle.writeFile(JSON.stringify(ledger));
    await handle.sync();
  } finally {
    await handle.close();
  }
}
async function hostedSignIn(
  page: Page,
  label: string,
  trigger: () => Promise<unknown>,
) {
  const popup = page.waitForEvent("popup");
  await trigger();
  const issuer = await popup;
  await issuer.waitForURL((url) => url.origin === ISSUER);
  const url = new URL(issuer.url());
  expect(
    url.searchParams.get("state")?.length,
    "OAuth state must satisfy the issuer minimum without weakening it",
  ).toBeGreaterThanOrEqual(16);
  await expect(
    issuer.getByRole("heading", { name: "Local engineering account" }),
  ).toBeVisible();
  expect(url.origin).toBe(ISSUER);
  expect(url.searchParams.get("code_challenge_method")).toBe("S256");
  expect(url.searchParams.get("code_challenge")).toMatch(/^[A-Za-z0-9_-]{43}$/);
  expect(url.searchParams.get("redirect_uri")).toBe("http://localhost:8082/");
  let formRedirectBlocked = false;
  const formStatuses: number[] = [];
  issuer.on("console", (message) => {
    if (message.text().includes("form-action")) formRedirectBlocked = true;
  });
  issuer.on("response", (response) => {
    if (
      response.url().startsWith(ISSUER + "/oauth2/authorize") &&
      response.request().method() === "POST"
    )
      formStatuses.push(response.status());
  });
  const closed = issuer.waitForEvent("close", { timeout: 15_000 });
  await issuer
    .getByRole("button", {
      name: `Use Fictional Browser ${label}`,
      exact: true,
    })
    .click({ noWaitAfter: true, timeout: 15_000 });
  try {
    await closed;
  } catch {
    const finalUrl = new URL(issuer.url());
    const diagnostics = await issuer.evaluate(() => ({
      ready: document.readyState,
      forms: document.forms.length,
      issuerRefused: document.body.innerText.includes(
        '"error":"invalid_request"',
      ),
      callbackCompleted: document.body.innerText.includes(
        "A check with context",
      ),
    }));
    throw new Error(
      `OAuth popup did not close: ${JSON.stringify({ origin: finalUrl.origin, path: finalUrl.pathname, queryKeys: [...finalUrl.searchParams.keys()], formRedirectBlocked, formStatuses, ...diagnostics })}`,
    );
  }
}
async function privacy(page: Page) {
  await page.getByRole("tab", { name: "Settings", exact: true }).click();
  await page
    .getByRole("button", {
      name: "Privacy & data. Local storage, export, deletion and upload retry preference",
    })
    .click();
}
async function notice(page: Page) {
  await expect(
    page.getByRole("heading", {
      name: /^(How your data is handled|A check with context)$/,
    }),
  ).toBeVisible();
  if (
    await page
      .getByRole("heading", { name: "How your data is handled" })
      .isVisible()
  ) {
    await page
      .getByRole("switch", { name: "I have read how this app handles data." })
      .check();
    await page.getByTestId("acknowledge-notice").click();
  }
}
function archiveEvidence(data: Buffer, sid: string) {
  expect(data.length).toBeLessThanOrEqual(64 * 1024 * 1024);
  const files = unzipSync(data),
    manifest = JSON.parse(Buffer.from(files["manifest.json"]!).toString());
  expect(manifest.session_ids).toEqual([sid]);
  expect(manifest.selection).toEqual({ kind: "single", session_ids: [sid] });
  expect(manifest.omitted_categories).toEqual(["raw_artifacts"]);
  expect(Object.keys(files).sort()).toEqual(
    [
      "manifest.json",
      ...manifest.files.map((entry: { path: string }) => entry.path),
    ].sort(),
  );
  expect(
    Object.keys(files).filter((name) => name.startsWith("checks/")),
  ).toEqual([`checks/${sid}.json`]);
  for (const entry of manifest.files) {
    const content = files[entry.path];
    expect(content, `Missing exported member ${entry.path}`).toBeDefined();
    expect(content!.length).toBe(entry.size_bytes);
    expect(createHash("sha256").update(content!).digest("hex")).toBe(
      entry.sha256,
    );
  }
  const saved = JSON.parse(
    Buffer.from(files[`checks/${sid}.json`]!).toString(),
  );
  expect(saved.session_id).toBe(sid);
  expect(saved.mode).toBe("synthetic");
  expect(saved.snapshot.profile.source).toBe("synthetic");
  expect(saved.snapshot.profile.age_years).toBeNull();
  expect(saved.result.state).toBe("measurement_only");
  expect(saved.result.probability).toBeNull();
  expect(saved.attempts.length).toBeGreaterThan(0);
  expect(
    saved.attempts.every(
      (attempt: { source: string }) => attempt.source === "simulated",
    ),
  ).toBe(true);
  return {
    sha256: createHash("sha256").update(data).digest("hex"),
    bytes: data.length,
    member_count: Object.keys(files).length,
  };
}

test("ordinary web completes owned PKCE, explicit upload, worker export, lost-ack recovery, reload and privacy boundaries", async ({
  page,
  context,
  request,
}, info) => {
  const ledger = await readLedger(),
    label = info.project.name === "live-mobile" ? "Mobile" : "Desktop";
  const account = `browser_${label.toLowerCase()}`;
  const study = ledger.governed?.[account];
  expect(
    study,
    "Run maintenance browser fixture --provision-governed before live acceptance",
  ).toBeDefined();
  const network = new Set<string>(),
    runtimeErrors: string[] = [];
  let sessionCreates = 0;
  let access = "",
    refresh = "",
    generation = 1,
    sid = "",
    owned = "";
  const evidence: Record<string, unknown> = {
    namespace: ledger.namespace,
    fictional_only: true,
    project: info.project.name,
    viewport: page.viewportSize(),
    origins: [API, ISSUER, "http://localhost:8082"],
  };
  page.on("pageerror", (error) => runtimeErrors.push(error.message));
  context.on("request", (req) => {
    network.add(new URL(req.url()).origin);
    if (req.url() === API + "/v1/sessions" && req.method() === "POST")
      sessionCreates++;
  });
  page.on("response", async (response) => {
    if (response.url() === ISSUER + "/oauth2/token" && response.ok()) {
      const body = await response.json();
      access = body.access_token;
      refresh = body.refresh_token ?? refresh;
    }
  });
  const api = async (
    method: string,
    path: string,
    data?: unknown,
    headers?: Record<string, string>,
  ) =>
    request.fetch(API + path, {
      method,
      headers: {
        Authorization: `Bearer ${access}`,
        "X-Data-Generation": String(generation),
        ...headers,
      },
      data,
    });
  const inventory = async () => {
    const response = await api("GET", "/v1/sessions?limit=100");
    expect(response.status()).toBe(200);
    const body = await response.json();
    expect(
      body.next_cursor,
      "Refuse deletion when history is not fully inventoried",
    ).toBeNull();
    const currentLedger = await readLedger();
    const known = currentLedger.accounts[account]!.session_ids;
    const profileResponse = await api("GET", "/v1/me/profile");
    expect(profileResponse.status()).toBe(200);
    const profile = await profileResponse.json();
    expect(
      profile.profile_version_id === null ||
        (currentLedger.profile_versions?.[account] ?? []).includes(
          profile.profile_version_id,
        ),
      "Unexpected existing profile: preserve it and stop",
    ).toBe(true);
    const capabilities = await (await api("GET", "/v1/me/capabilities")).json();
    expect(
      capabilities.studies.every(
        (consent: { study_id: string }) => consent.study_id === study!.study_id,
      ),
      "Unexpected study consent: preserve it and stop",
    ).toBe(true);
    expect(
      body.items.every((item: { session_id: string }) =>
        known.includes(item.session_id),
      ),
      "Unexpected existing records: preserve account and stop before deletion",
    ).toBe(true);
    return body.items as { session_id: string }[];
  };
  try {
    const configResponse = await request.get(API + "/v1/app-config");
    expect(configResponse.status(), "Live API prerequisite unavailable").toBe(
      200,
    );
    const config = await configResponse.json();
    expect(config.auth.issuer).toBe(ISSUER);
    expect(config.auth.redirect_uris).toContain("http://localhost:8082/");
    expect(config.inference_available).toBe(false);
    expect(
      (await request.get(ISSUER + "/health/live")).status(),
      "Live issuer prerequisite unavailable",
    ).toBe(200);
    await page.goto("/");
    await expect(page.getByTestId("sign-in")).toBeVisible();
    await hostedSignIn(page, label, () => page.getByTestId("sign-in").click());
    await expect.poll(() => !!access).toBe(true);
    let capsResponse = await api("GET", "/v1/me/capabilities");
    expect(capsResponse.status()).toBe(200);
    let caps = await capsResponse.json();
    owned = caps.account_ref;
    generation = caps.data_generation;
    if (caps.account_state === "deletion_pending") {
      await expect
        .poll(
          async () => {
            caps = await (await api("GET", "/v1/me/capabilities")).json();
            return caps.account_state;
          },
          { timeout: 90_000, intervals: [1000, 2000] },
        )
        .toBe("awaiting_generation_ack");
    }
    if (caps.account_state === "awaiting_generation_ack") {
      await expect(
        page.getByRole("button", {
          name: "Start a new empty workspace",
          exact: true,
        }),
      ).toBeVisible();
      await page
        .getByRole("button", {
          name: "Start a new empty workspace",
          exact: true,
        })
        .click();
      const priorAckEvent = page.waitForResponse(
        (r) =>
          r.url() === API + "/v1/me/data-generation/acknowledgments" &&
          r.request().method() === "POST",
      );
      await page
        .getByRole("dialog")
        .getByRole("button", { name: "Start new empty workspace", exact: true })
        .click();
      expect((await priorAckEvent).status()).toBe(200);
      caps = await (await api("GET", "/v1/me/capabilities")).json();
      generation = caps.data_generation;
      evidence.prior_completed_deletion_recovered = true;
    }
    expect(
      caps.account_state,
      "Prior privacy work requires explicit recovery",
    ).toBe("active");
    await inventory();
    await notice(page);
    await expect(
      page.getByRole("heading", { name: "A check with context" }),
    ).toBeVisible();
    await page.getByTestId("review-context").click();
    await page
      .getByRole("button", { name: "Edit profile and context", exact: true })
      .click();
    await page.getByLabel("Age (years)", { exact: true }).fill("31");
    const profileSaved = page.waitForResponse(
      (r) =>
        r.url() === API + "/v1/me/profile" && r.request().method() === "PATCH",
    );
    await page.getByTestId("save-profile").click();
    const profileResponse = await profileSaved;
    expect(profileResponse.status()).toBe(200);
    await rememberSession(
      account,
      (await profileResponse.json()).profile_version_id,
      true,
    );
    await page.getByRole("tab", { name: "Home", exact: true }).click();
    await page.getByTestId("review-context").click();
    await page
      .getByRole("radio", {
        name: "Fictional engineering fixture",
        exact: true,
      })
      .click();
    await page
      .getByRole("switch", { name: "I have reviewed this check’s context." })
      .check();
    await page.getByTestId("start-check").click();
    await page.getByRole("button", { name: "3 Saliva", exact: true }).click();
    await page.getByTestId("simulate-saliva").click();
    await page.getByRole("button", { name: "8 Review", exact: true }).click();
    await page.getByTestId("save-check").click();
    await expect(
      page.getByRole("heading", { name: "Measurements saved" }),
    ).toBeVisible();
    expect(
      sessionCreates,
      "Saving alone must not create a server session",
    ).toBe(0);
    const beforeUpload = await inventory();
    await expect(page.getByTestId("upload-check")).toBeVisible();
    // Send the actual request, then drop its accepted acknowledgement. Never fabricate success.
    let finalizeKey = "";
    let dropped = false,
      accepted: Record<string, unknown> | null = null;
    await page.route(
      API + "/v1/sessions/*/finalize",
      async (route) => {
        finalizeKey = route.request().headers()["idempotency-key"]!;
        const response = await route.fetch({ maxRetries: 0 });
        expect(response.status()).toBe(202);
        accepted = await response.json();
        dropped = true;
        await route.abort("connectionreset");
      },
      { times: 1 },
    );
    const createdEvent = page.waitForResponse(
      (r) =>
        r.url() === API + "/v1/sessions" && r.request().method() === "POST",
    );
    await page.getByTestId("upload-check").click();
    await page
      .getByRole("dialog")
      .getByRole("button", { name: "Upload check", exact: true })
      .click();
    const created = await createdEvent;
    expect(created.status()).toBe(201);
    sid = (await created.json()).session_id;
    await rememberSession(account, sid);
    await expect.poll(() => dropped).toBe(true);
    expect(accepted).not.toBeNull();
    evidence.finalize = accepted;
    expect(beforeUpload.some((item) => item.session_id === sid)).toBe(false);
    const queuedResult = await api("GET", `/v1/sessions/${sid}/result`);
    expect([200, 202]).toContain(queuedResult.status());
    await page.getByRole("tab", { name: "History", exact: true }).click();
    const replayEvent = page.waitForResponse(
      (r) =>
        r.url() === `${API}/v1/sessions/${sid}/finalize` &&
        r.request().method() === "POST",
    );
    await page
      .getByRole("button", {
        name: "Retry requested operations now",
        exact: true,
      })
      .click();
    const replay = await replayEvent;
    expect(replay.status()).toBe(202);
    expect(replay.request().headers()["idempotency-key"]).toBe(finalizeKey);
    expect(await replay.json()).toEqual(accepted);
    evidence.finalize_receipt_replayed = true;
    await expect
      .poll(
        async () => (await api("GET", `/v1/sessions/${sid}/result`)).status(),
        { timeout: 90_000, intervals: [500, 1000, 2000] },
      )
      .toBe(200);
    const result = await (
      await api("GET", `/v1/sessions/${sid}/result`)
    ).json();
    expect(result.state).toBe("measurement_only");
    expect(result.probability).toBeNull();
    evidence.result = {
      state: result.state,
      probability: result.probability,
      session_id: sid,
    };
    await page.reload();
    await expect(page.getByTestId("sign-in")).toBeVisible();
    await expect(
      page.getByRole("tab", { name: "History", exact: true }),
    ).toHaveCount(0);
    await hostedSignIn(page, label, () => page.getByTestId("sign-in").click());
    await notice(page);
    await page.getByRole("tab", { name: "History", exact: true }).click();
    await expect(
      page.getByText("Your first check starts here", { exact: true }),
    ).toBeVisible();
    await page
      .getByRole("button", { name: "Refresh synced history", exact: true })
      .click();
    await expect(
      page.getByText("Synced metadata", { exact: true }).first(),
    ).toBeVisible();
    await page.getByLabel("Find by check ID", { exact: true }).fill(sid);
    await page
      .getByRole("button", {
        name: new RegExp(`${sid.slice(0, 8)}…${sid.slice(-6)}$`),
      })
      .click();
    await expect(
      page.getByRole("heading", { name: "Measurements saved" }),
    ).toBeVisible();
    await page
      .getByRole("button", {
        name: "Export this check. Exactly this check and its associated evidence",
      })
      .click();
    await page
      .getByRole("radio", { name: "Synced records", exact: true })
      .click();
    await page
      .getByRole("switch", {
        name: "I have reviewed the source and selected data.",
      })
      .check();
    await page.getByTestId("create-export").click();
    const exportEvent = page.waitForResponse(
      (r) =>
        r.url() === API + "/v1/privacy/exports" &&
        r.request().method() === "POST",
    );
    await page
      .getByRole("dialog")
      .getByRole("button", { name: "Request export", exact: true })
      .click();
    const exportResponse = await exportEvent;
    expect(exportResponse.status()).toBe(202);
    const exported = await exportResponse.json();
    evidence.export = exported;
    await expect
      .poll(
        async () =>
          (
            await (
              await api("GET", `/v1/privacy/jobs/${exported.job_id}`)
            ).json()
          ).state,
        { timeout: 90_000, intervals: [500, 1000, 2000] },
      )
      .toBe("completed");
    await page
      .getByRole("button", { name: "Refresh request status", exact: true })
      .click();
    await page
      .getByRole("button", { name: "Download and share export", exact: true })
      .click();
    const downloadEvent = page.waitForEvent("download");
    await page
      .getByRole("dialog")
      .getByRole("button", {
        name: "Download and open share sheet",
        exact: true,
      })
      .click();
    const download = await downloadEvent,
      downloadPath = info.outputPath("fictional-structured-export.zip");
    await download.saveAs(downloadPath);
    evidence.archive = archiveEvidence(await readFile(downloadPath), sid);
    const foreignContext = await context.browser()!.newContext(),
      foreignPage = await foreignContext.newPage();
    let foreignAccess = "";
    foreignPage.on("response", async (response) => {
      if (response.url() === ISSUER + "/oauth2/token" && response.ok())
        foreignAccess = (await response.json()).access_token;
    });
    await foreignPage.goto("http://localhost:8082/");
    await hostedSignIn(
      foreignPage,
      label === "Mobile" ? "Desktop" : "Mobile",
      () => foreignPage.getByTestId("sign-in").click(),
    );
    await expect.poll(() => !!foreignAccess).toBe(true);
    for (const path of [
      `/v1/sessions/${sid}`,
      `/v1/privacy/jobs/${exported.job_id}/download`,
    ]) {
      expect(
        (
          await request.get(API + path, {
            headers: { Authorization: `Bearer ${foreignAccess}` },
          })
        ).status(),
      ).toBe(404);
    }
    await foreignContext.close();
    await page.bringToFront();
    if (await page.getByTestId("unlock-records").isVisible())
      await page.getByTestId("unlock-records").click();
    await page.getByRole("tab", { name: "Settings", exact: true }).click();
    await page
      .getByRole("button", {
        name: "Research access. Separate study invitation and consent; no automatic enrollment",
      })
      .click();
    const studyCard = page
      .getByText(study!.study_id, { exact: true })
      .locator("../..");
    await studyCard
      .getByRole("button", {
        name: "Read complete study information",
        exact: true,
      })
      .click();
    await studyCard
      .getByRole("switch", { name: "I consent to this exact study document." })
      .check();
    await studyCard
      .getByRole("button", {
        name: "Reauthenticate and record study consent",
        exact: true,
      })
      .click();
    const consentEvent = page.waitForResponse(
      (r) =>
        r.url() === `${API}/v1/studies/${study!.study_id}/consents` &&
        r.request().method() === "POST",
    );
    await hostedSignIn(page, label, () =>
      page
        .getByRole("dialog")
        .getByRole("button", {
          name: "Reauthenticate and consent",
          exact: true,
        })
        .click(),
    );
    const consentResponse = await consentEvent;
    expect(consentResponse.status()).toBe(201);
    const consent = await consentResponse.json();
    expect(consent.document_sha256).toBe(study!.document_sha256);
    expect(consent.state).toBe("active");
    evidence.consent = {
      study_id: consent.study_id,
      consent_record_id: consent.consent_record_id,
      state: consent.state,
      document_sha256: consent.document_sha256,
    };
    const researchSid = randomUUID();
    const admitted = await api(
      "POST",
      "/v1/sessions",
      {
        session_id: researchSid,
        mode: "controlled_research",
        study_id: study!.study_id,
        protocol_id: study!.protocol_id,
      },
      { "Idempotency-Key": randomUUID() },
    );
    expect(admitted.status()).toBe(201);
    await rememberSession(account, researchSid);
    await expect(
      studyCard.getByText("Current consent recorded", { exact: true }),
    ).toBeVisible();
    await studyCard
      .getByRole("button", { name: "Withdraw from this study", exact: true })
      .click();
    const withdrawalEvent = page.waitForResponse(
      (r) =>
        r.url() === `${API}/v1/studies/${study!.study_id}/withdrawals` &&
        r.request().method() === "POST",
    );
    await page
      .getByRole("dialog")
      .getByRole("button", {
        name: "Stop local work and request withdrawal",
        exact: true,
      })
      .click();
    const withdrawnResponse = await withdrawalEvent;
    expect(withdrawnResponse.status()).toBe(200);
    const withdrawn = await withdrawnResponse.json();
    expect(withdrawn.state).toBe("withdrawn");
    evidence.withdrawal = withdrawn;
    const denied = await api(
      "POST",
      "/v1/sessions",
      {
        session_id: randomUUID(),
        mode: "controlled_research",
        study_id: study!.study_id,
        protocol_id: study!.protocol_id,
      },
      { "Idempotency-Key": randomUUID() },
    );
    expect(denied.status()).toBe(403);
    expect((await denied.json()).code).toBe("CAPABILITY_DENIED");
    await page
      .getByRole("button", {
        name: "Refresh invitations and membership",
        exact: true,
      })
      .click();
    await expect(
      studyCard.getByText("New invitation required", { exact: true }),
    ).toBeVisible();
    evidence.withdrawn_consent_denied = true;
    await inventory();
    const oldAccess = access,
      oldGeneration = generation;
    await privacy(page);
    await page
      .getByRole("button", { name: "Delete all synced data", exact: true })
      .click();
    await hostedSignIn(page, label, () =>
      page
        .getByRole("dialog")
        .getByRole("button", {
          name: "Reauthenticate and request data deletion",
          exact: true,
        })
        .click(),
    );
    let acceptedDeletion: { job_id: string } | null = null;
    await page.route(
      API + "/v1/privacy/deletion-requests",
      async (route) => {
        const response = await route.fetch({ maxRetries: 0 });
        expect(response.status()).toBe(202);
        acceptedDeletion = await response.json();
        await route.abort("connectionreset");
      },
      { times: 1 },
    );
    await page
      .getByRole("dialog")
      .getByRole("button", { name: "Request deletion", exact: true })
      .click();
    await expect.poll(() => acceptedDeletion !== null).toBe(true);
    await expect(
      page.getByText("Pending deletion intent", { exact: true }),
    ).toBeVisible();
    const deletion = acceptedDeletion! as { job_id: string };
    evidence.deletion = deletion;
    evidence.pending_deletion_after_lost_ack = true;
    generation = oldGeneration + 1;
    await expect
      .poll(
        async () =>
          (
            await (
              await api("GET", `/v1/privacy/jobs/${deletion.job_id}`)
            ).json()
          ).state,
        { timeout: 90_000, intervals: [500, 1000, 2000] },
      )
      .toBe("completed");
    const stale = await request.post(API + "/v1/sessions", {
      headers: {
        Authorization: `Bearer ${oldAccess}`,
        "X-Data-Generation": String(oldGeneration),
        "Idempotency-Key": randomUUID(),
      },
      data: { session_id: randomUUID(), mode: "synthetic", protocol_id: null },
    });
    expect([403, 410]).toContain(stale.status());
    expect([403, 404, 410]).toContain(
      (
        await api("GET", `/v1/privacy/jobs/${exported.job_id}/download`)
      ).status(),
    );
    await page.reload();
    await expect(page.getByTestId("sign-in")).toBeVisible();
    await hostedSignIn(page, label, () => page.getByTestId("sign-in").click());
    await expect(
      page.getByRole("button", {
        name: "Start a new empty workspace",
        exact: true,
      }),
    ).toBeVisible();
    await page
      .getByRole("button", { name: "Start a new empty workspace", exact: true })
      .click();
    const generationAckEvent = page.waitForResponse(
      (r) =>
        r.url() === API + "/v1/me/data-generation/acknowledgments" &&
        r.request().method() === "POST",
    );
    await page
      .getByRole("dialog")
      .getByRole("button", { name: "Start new empty workspace", exact: true })
      .click();
    expect((await generationAckEvent).status()).toBe(200);
    capsResponse = await api("GET", "/v1/me/capabilities");
    caps = await capsResponse.json();
    expect(caps.account_ref).toBe(owned);
    expect(caps.account_state).toBe("active");
    generation = caps.data_generation;
    expect(await inventory()).toEqual([]);
    await page.getByRole("tab", { name: "Settings", exact: true }).click();
    await page.getByRole("button", { name: "Sign out", exact: true }).click();
    const refreshBeforeLogout = refresh;
    const providerRevokedEvent = page.waitForResponse(
      (r) =>
        r.url() === ISSUER + "/oauth2/revoke" &&
        r.request().method() === "POST",
    );
    const logoutEvent = page.waitForResponse(
      (r) =>
        r.url() === API + "/v1/auth/logout" && r.request().method() === "POST",
    );
    await page
      .getByRole("dialog")
      .getByRole("button", { name: "Keep records and sign out", exact: true })
      .click();
    const logoutResponse = await logoutEvent;
    expect(logoutResponse.status()).toBe(200);
    const logout = await logoutResponse.json();
    expect(logout.remote_family_revoked).toBe(true);
    evidence.logout = logout;
    expect((await providerRevokedEvent).status()).toBe(200);
    expect(
      (
        await request.post(ISSUER + "/oauth2/token", {
          form: {
            grant_type: "refresh_token",
            client_id: config.auth.client_id,
            refresh_token: refreshBeforeLogout,
          },
        })
      ).status(),
    ).toBe(400);
    await expect(page.getByTestId("sign-in")).toBeVisible();
    expect(runtimeErrors).toEqual([]);
    expect(
      [...network].every((origin) =>
        [API, ISSUER, "http://localhost:8082"].includes(origin),
      ),
    ).toBe(true);
    evidence.memory_only_reload = true;
    evidence.foreign_denied = true;
    evidence.retired_generation_denied = true;
    evidence.revoked_refresh_denied = true;
  } finally {
    evidence.network_destinations = [...network].sort();
    await writeFile(
      info.outputPath("redacted-live-receipts.json"),
      JSON.stringify(evidence, null, 2),
      { mode: 0o600 },
    );
    await info.attach("redacted-live-receipts", {
      body: JSON.stringify(evidence, null, 2),
      contentType: "application/json",
    });
  }
});
