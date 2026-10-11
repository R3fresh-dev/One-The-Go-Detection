import { test, expect } from "@playwright/test";
import { createHash } from "node:crypto";
import { readFile } from "node:fs/promises";
import { unzipSync } from "fflate";

test("guest completes a measurement-only check, exact export and privacy/settings journey", async ({
  page,
}, info) => {
  const runtimeErrors: string[] = [];
  page.on("pageerror", (e) => runtimeErrors.push(e.message));
  // The offline demo remains independent of account services, permissions and sign-in.
  await page.route("http://{localhost,127.0.0.1}:8000/**", (route) =>
    route.abort("internetdisconnected"),
  );
  await page.goto("/");
  await expect(
    page.getByRole("heading", { name: "Your measurements, in one place" }),
  ).toBeVisible();
  await page.getByTestId("explore-demo").click();
  await page.getByRole("button", { name: "Start demo", exact: true }).click();
  await expect(
    page.getByRole("button", { name: "Continue", exact: true }),
  ).toBeDisabled();
  await page
    .getByRole("switch", { name: "I have read how this app handles data." })
    .check();
  await page.getByTestId("acknowledge-notice").click();
  await expect(
    page.getByRole("heading", { name: "A check with context" }),
  ).toBeVisible();
  await expect(page.getByTestId("review-context")).toBeInViewport();
  await page.screenshot({
    path: `artifacts/${info.project.name}-home.png`,
    fullPage: true,
  });
  await page.getByTestId("review-context").click();
  await page
    .getByRole("switch", { name: "I have reviewed this check’s context." })
    .check();
  await page.getByTestId("start-check").click();
  await page.getByRole("button", { name: "3 Saliva", exact: true }).click();
  await page.getByTestId("simulate-saliva").click();
  await page.getByRole("button", { name: "4 Eyes", exact: true }).click();
  await page
    .getByRole("button", { name: "Add fictional eye example", exact: true })
    .click();
  await page.getByRole("button", { name: "6 ECG", exact: true }).click();
  await page
    .getByRole("button", { name: "Add fictional ECG example", exact: true })
    .click();
  await page.getByRole("button", { name: "7 Reaction", exact: true }).click();
  await expect(
    page.getByText("Native task unavailable:", { exact: false }),
  ).toBeVisible();
  await expect(page.getByTestId("start-native-task")).toBeDisabled();
  await page.getByRole("button", { name: "8 Review", exact: true }).click();
  await page.getByTestId("save-check").click();
  await expect(
    page.getByRole("heading", { name: "Measurements saved" }),
  ).toBeVisible();
  await expect(page.getByTestId("upload-check")).toHaveCount(0);
  await expect(
    page.getByText("local finalized", { exact: true }),
  ).toBeVisible();
  await page.screenshot({
    path: `artifacts/${info.project.name}-result.png`,
    fullPage: true,
  });
  await page
    .getByRole("button", {
      name: "Export this check. Exactly this check and its associated evidence",
    })
    .click();
  await expect(
    page.getByText("Exactly one check", { exact: true }),
  ).toBeVisible();
  await page
    .getByRole("switch", {
      name: "I have reviewed the source and selected data.",
    })
    .check();
  await page.getByTestId("create-export").click();
  const download = page.waitForEvent("download");
  await page
    .getByRole("button", { name: "Create export and share", exact: true })
    .click();
  const archive = await download;
  expect(archive.suggestedFilename()).toMatch(/\.zip$/);
  const archivePath = info.outputPath("selected-check.zip");
  await archive.saveAs(archivePath);
  const files = unzipSync(await readFile(archivePath));
  const manifest = JSON.parse(Buffer.from(files["manifest.json"]!).toString());
  expect(manifest.selection.kind).toBe("single");
  expect(manifest.session_ids).toHaveLength(1);
  expect(manifest.selection.session_ids).toEqual(manifest.session_ids);
  expect(manifest.raw_artifacts_included).toBe(false);
  expect(manifest.canonicalization).toBe("RFC8785");
  for (const entry of manifest.files) {
    const content = files[entry.path];
    expect(content, `Missing exported file ${entry.path}`).toBeDefined();
    expect(content!.length).toBe(entry.bytes);
    expect(createHash("sha256").update(content!).digest("hex")).toBe(
      entry.sha256,
    );
  }
  expect(
    Object.keys(files).filter((name) => name.startsWith("checks/")),
  ).toEqual([`checks/${manifest.session_ids[0]}.json`]);
  const saved = JSON.parse(
    Buffer.from(files[`checks/${manifest.session_ids[0]}.json`]!).toString(),
  );
  expect(saved.source).toBe("guest_demo");
  expect(saved.result.state).toBe("measurement_only");
  expect(saved.result.probability).toBeNull();
  expect(files[`contexts/${manifest.session_ids[0]}.json`]).toBeDefined();
  expect(files[`manifests/${manifest.session_ids[0]}.json`]).toBeDefined();
  await page.getByRole("tab", { name: "Settings", exact: true }).click();
  await page.getByRole("radio", { name: "Dark", exact: true }).click();
  await page
    .getByRole("button", {
      name: "Privacy & data. Local storage, export, deletion and upload retry preference",
    })
    .click();
  await expect(
    page.getByRole("switch", { name: "Retry queued uploads automatically" }),
  ).not.toBeChecked();
  await expect(
    page.getByRole("button", { name: "Delete account", exact: true }),
  ).toHaveCount(0);
  await page.getByRole("tab", { name: "Settings", exact: true }).click();
  await page
    .getByRole("button", {
      name: "Research access. Separate study invitation and consent; no automatic enrollment",
    })
    .click();
  await expect(
    page.getByRole("heading", { name: "No automatic enrollment" }),
  ).toBeVisible();
  expect(runtimeErrors).toEqual([]);
});

test("live device status, invalid synthetic ECG evidence and bidirectional replacement navigation remain explicit", async ({
  page,
}) => {
  const runtimeErrors: string[] = [];
  page.on("pageerror", (error) => runtimeErrors.push(error.message));
  await page.route("http://{localhost,127.0.0.1}:8000/**", (route) =>
    route.abort("internetdisconnected"),
  );
  await page.goto("/");
  await page.getByTestId("explore-demo").click();
  await page.getByRole("button", { name: "Start demo", exact: true }).click();
  await page
    .getByRole("switch", { name: "I have read how this app handles data." })
    .check();
  await page.getByTestId("acknowledge-notice").click();
  await expect(page.getByTestId("review-context")).toBeInViewport();
  await page.getByTestId("home-device-connection").click();
  await page
    .getByRole("button", { name: "Use local synthetic simulator", exact: true })
    .click();
  await expect(
    page.getByText("Synthetic simulator connected", { exact: true }),
  ).toBeVisible();
  await page.getByRole("tab", { name: "Home", exact: true }).click();
  await expect(
    page.getByRole("heading", {
      name: "Synthetic reader connected",
      exact: true,
    }),
  ).toBeVisible();
  await page.getByTestId("review-context").click();
  await page
    .getByRole("switch", { name: "I have reviewed this check’s context." })
    .check();
  await page.getByTestId("start-check").click();
  await page.getByRole("button", { name: "6 ECG", exact: true }).click();
  await page.getByRole("radio", { name: "Contact lost", exact: true }).click();
  await page
    .getByRole("button", {
      name: "Start ECG software demonstration",
      exact: true,
    })
    .click();
  await expect(
    page.getByText("Fictional contact lost", { exact: true }),
  ).toBeVisible();
  await expect(
    page.getByText("Synthetic signal quality failed.", { exact: false }),
  ).toBeVisible();
  await page.getByRole("button", { name: "8 Review", exact: true }).click();
  await page.getByTestId("save-check").click();
  await expect(
    page.getByRole("heading", { name: "Measurements saved" }),
  ).toBeVisible();
  await page
    .getByRole("button", { name: "Start a replacement check", exact: true })
    .click();
  await page
    .getByRole("button", {
      name: "Review current context on Home",
      exact: true,
    })
    .click();
  await page.getByTestId("review-context").click();
  await page
    .getByRole("switch", { name: "I have reviewed this check’s context." })
    .check();
  await page.getByTestId("start-check").click();
  await page.getByRole("button", { name: "8 Review", exact: true }).click();
  await page.getByTestId("save-check").click();
  await page.getByTestId("view-original-check").click();
  await expect(
    page.getByText("This record does not replace an earlier acquisition.", {
      exact: true,
    }),
  ).toBeVisible();
  await page.getByRole("button", { name: /^View replacement check / }).click();
  await expect(
    page.getByText("This check replaces an earlier acquisition", {
      exact: true,
    }),
  ).toBeVisible();
  expect(runtimeErrors).toEqual([]);
});

test("profile errors remain actionable and browser reload never pretends encrypted persistence", async ({
  page,
}) => {
  await page.route("http://{localhost,127.0.0.1}:8000/**", (route) =>
    route.abort("internetdisconnected"),
  );
  await page.goto("/");
  await page.getByTestId("explore-demo").click();
  await page.getByRole("button", { name: "Start demo", exact: true }).click();
  await page
    .getByRole("switch", { name: "I have read how this app handles data." })
    .check();
  await page.getByTestId("acknowledge-notice").click();
  await page.getByTestId("review-context").click();
  await page
    .getByRole("button", { name: "Edit profile and context", exact: true })
    .click();
  await page
    .getByRole("textbox", { name: "Age (years)", exact: true })
    .fill("17");
  await page.getByTestId("save-profile").click();
  await expect(
    page
      .getByText("Age must be a whole number from 18 to 125, or blank.", {
        exact: true,
      })
      .first(),
  ).toBeVisible();
  await page
    .getByRole("textbox", { name: "Age (years)", exact: true })
    .fill("");
  await page
    .getByRole("textbox", { name: "Height (cm)", exact: true })
    .fill("180");
  await page
    .getByRole("textbox", { name: "Weight (kg)", exact: true })
    .fill("80");
  await expect(page.getByText("24.7 kg/m²", { exact: true })).toBeVisible();
  await page.getByTestId("save-profile").click();
  await expect(
    page.getByText("Profile saved on this device.", { exact: true }),
  ).toBeVisible();
  await page.reload();
  await expect(
    page.getByRole("heading", { name: "Your measurements, in one place" }),
  ).toBeVisible();
  await expect(
    page.getByText("Browser preview · memory only", { exact: true }),
  ).toBeVisible();
});
