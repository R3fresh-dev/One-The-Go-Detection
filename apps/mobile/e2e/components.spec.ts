import { test, expect, type Page } from "@playwright/test";

// These are real React Native Web DOM component checks against the exported
// production application. Offline guest fixtures are never live-dependency proof.
async function enterGuest(page: Page) {
  await page.route("http://{localhost,127.0.0.1}:8000/**", (route) =>
    route.abort("internetdisconnected"),
  );
  await page.goto("/");
  await page.getByTestId("explore-demo").click();
  await page.getByRole("button", { name: "Start demo", exact: true }).click();
}

async function acknowledgeNotice(page: Page) {
  await page
    .getByRole("switch", { name: "I have read how this app handles data." })
    .check();
  await page.getByTestId("acknowledge-notice").click();
  await expect(
    page.getByRole("heading", { name: "A check with context" }),
  ).toBeVisible();
}

async function saveEmptyCheck(page: Page) {
  await page.getByTestId("review-context").click();
  await page
    .getByRole("switch", { name: "I have reviewed this check’s context." })
    .check();
  await page.getByTestId("start-check").click();
  await page.getByRole("button", { name: "8 Review", exact: true }).click();
  await page.getByTestId("save-check").click();
  await expect(
    page.getByRole("heading", { name: "Measurements saved" }),
  ).toBeVisible();
}

async function openPrivacy(page: Page) {
  await page.getByRole("tab", { name: "Settings", exact: true }).click();
  await page
    .getByRole("button", {
      name: "Privacy & data. Local storage, export, deletion and upload retry preference",
    })
    .click();
}

test("notice and context components require separate explicit acknowledgments", async ({
  page,
}) => {
  await enterGuest(page);
  const notice = page.getByRole("switch", {
    name: "I have read how this app handles data.",
  });
  await expect(notice).not.toBeChecked();
  await expect(page.getByTestId("acknowledge-notice")).toBeDisabled();
  await expect(
    page.getByText("Verified plain text", { exact: true }),
  ).toBeVisible();
  await page
    .getByRole("button", { name: "Privacy controls", exact: true })
    .click();
  await expect(
    page.getByRole("heading", { name: "Privacy & data" }),
  ).toBeVisible();
  await page
    .getByRole("button", { name: "Read application data notice", exact: true })
    .click();
  await expect(notice).not.toBeChecked();
  await acknowledgeNotice(page);
  await page.getByTestId("review-context").click();
  await expect(page.getByTestId("start-check")).toBeDisabled();
  await expect(
    page.getByRole("switch", { name: "I have reviewed this check’s context." }),
  ).not.toBeChecked();
  await expect(
    page.getByRole("button", { name: "Edit profile and context", exact: true }),
  ).toBeEnabled();
});

test("profile fields announce validation, preserve canonical units and guard unsaved edits", async ({
  page,
}) => {
  await enterGuest(page);
  await acknowledgeNotice(page);
  await page.getByTestId("review-context").click();
  await page
    .getByRole("button", { name: "Edit profile and context", exact: true })
    .click();
  const age = page.getByRole("textbox", { name: "Age (years)", exact: true });
  await age.fill("17");
  await page.getByTestId("save-profile").click();
  await expect(age).toBeFocused();
  await expect(age).toHaveAttribute("aria-invalid", "true");
  await expect(page.getByRole("alert").first()).toContainText("18 to 125");
  await age.fill("29");
  await page
    .getByRole("textbox", { name: "Height (cm)", exact: true })
    .fill("180");
  await page
    .getByRole("textbox", { name: "Weight (kg)", exact: true })
    .fill("80");
  await page.getByRole("radio", { name: "ft + in / lb", exact: true }).click();
  await expect(
    page.getByRole("textbox", { name: "Height (whole feet)", exact: true }),
  ).toHaveValue("5");
  await expect(
    page.getByRole("textbox", { name: "Weight (lb)", exact: true }),
  ).toHaveValue("176.37");
  await page.getByRole("radio", { name: "cm / kg", exact: true }).click();
  await expect(
    page.getByRole("textbox", { name: "Height (cm)", exact: true }),
  ).toHaveValue("180");
  await expect(
    page.getByRole("textbox", { name: "Weight (kg)", exact: true }),
  ).toHaveValue("80");
  await page.getByRole("button", { name: "‹ Back", exact: true }).click();
  await expect(
    page.getByRole("heading", { name: "Leave without saving this profile?" }),
  ).toBeVisible();
  await page.getByRole("button", { name: "Cancel", exact: true }).click();
  await expect(age).toHaveValue("29");
  await page.getByTestId("save-profile").click();
  await expect(
    page.getByText("Profile saved on this device.", { exact: true }),
  ).toBeVisible();
});

test("confirmation components never enable retry or erase unsynced records on cancellation", async ({
  page,
}) => {
  await enterGuest(page);
  await acknowledgeNotice(page);
  await saveEmptyCheck(page);
  await openPrivacy(page);
  const retry = page.getByRole("switch", {
    name: "Retry queued uploads automatically",
  });
  // This controlled switch opens consent first; it deliberately remains off.
  await retry.click();
  await expect(
    page.getByRole("heading", { name: "Enable automatic retries?" }),
  ).toBeVisible();
  await expect(
    page.getByRole("dialog", { name: "Enable automatic retries?" }),
  ).toBeVisible();
  await expect(
    page.getByRole("tab", { name: "History", exact: true }),
  ).toHaveCount(0);
  await page.getByRole("button", { name: "Cancel", exact: true }).click();
  await expect(retry).not.toBeChecked();
  await page
    .getByRole("button", { name: "Clear local records", exact: true })
    .click();
  await expect(
    page.getByRole("heading", {
      name: "Clear this workspace’s local records?",
    }),
  ).toBeVisible();
  // The first destructive confirmation opens a second, explicit unsynced-data warning.
  await page
    .getByRole("button", { name: "Clear local records", exact: true })
    .click();
  await expect(
    page.getByRole("heading", { name: "Discard 1 unsynced checks?" }),
  ).toBeVisible();
  await page.getByRole("button", { name: "Cancel", exact: true }).click();
  await page.getByRole("tab", { name: "History", exact: true }).click();
  await expect(
    page.getByText("local finalized", { exact: true }),
  ).toBeVisible();
  await expect(
    page.getByRole("heading", { name: "Your first check starts here" }),
  ).toHaveCount(0);
});

test("history selection remains exact when filters hide selected records", async ({
  page,
}) => {
  await enterGuest(page);
  await acknowledgeNotice(page);
  await saveEmptyCheck(page);
  await page.getByRole("tab", { name: "History", exact: true }).click();
  await page
    .getByRole("switch", { name: "Select saved checks to export" })
    .check();
  await expect(
    page.getByRole("button", { name: "Review selected export", exact: true }),
  ).toBeDisabled();
  await page.getByRole("switch", { name: /^Select [0-9a-f]/ }).check();
  await page
    .getByRole("textbox", { name: "Find by check ID", exact: true })
    .fill("no-match");
  await expect(
    page.getByRole("heading", { name: "No matching checks" }),
  ).toBeVisible();
  await expect(page.getByText("1 checks", { exact: true })).toBeVisible();
  await page
    .getByRole("button", { name: "Review selected export", exact: true })
    .click();
  await expect(
    page.getByText("Exactly one check", { exact: true }),
  ).toBeVisible();
  await expect(page.getByTestId("create-export")).toBeDisabled();
  await page
    .getByRole("button", { name: "Choose all records instead", exact: true })
    .click();
  await expect(
    page.getByRole("heading", {
      name: "Replace the exact check selection with all records?",
    }),
  ).toBeVisible();
  await page.getByRole("button", { name: "Cancel", exact: true }).click();
  await expect(
    page.getByText("Exactly one check", { exact: true }),
  ).toBeVisible();
});

test("navigation and theme components expose selected state at both viewport sizes", async ({
  page,
}) => {
  await enterGuest(page);
  await acknowledgeNotice(page);
  const home = page.getByRole("tab", { name: "Home", exact: true });
  await expect(home).toHaveAttribute("aria-selected", "true");
  const settings = page.getByRole("tab", { name: "Settings", exact: true });
  await settings.focus();
  await page.keyboard.press("Enter");
  await expect(settings).toHaveAttribute("aria-selected", "true");
  await expect(home).toHaveAttribute("aria-selected", "false");
  const heading = page.getByRole("heading", { name: "Settings", exact: true });
  const oldColor = await heading.evaluate(
    (element) => getComputedStyle(element).color,
  );
  const dark = page.getByRole("radio", { name: "Dark", exact: true });
  await dark.click();
  await expect(dark).toBeChecked();
  await expect
    .poll(() => heading.evaluate((element) => getComputedStyle(element).color))
    .not.toBe(oldColor);
  await page
    .getByRole("switch", { name: "Reduce motion", exact: true })
    .check();
  await expect(
    page.getByRole("switch", { name: "Reduce motion", exact: true }),
  ).toBeChecked();
  for (const tab of await page.getByRole("tab").all()) {
    const bounds = await tab.boundingBox();
    expect(bounds).not.toBeNull();
    expect(bounds!.width).toBeGreaterThanOrEqual(44);
    expect(bounds!.height).toBeGreaterThanOrEqual(44);
  }
  expect(
    await page.evaluate(() => document.documentElement.scrollWidth),
  ).toBeLessThanOrEqual(page.viewportSize()!.width);
});

test("Settings and Back preserve the actual draft and collected example without a camera prompt", async ({
  page,
}) => {
  await page.addInitScript(() => {
    (window as any).cameraRequests = 0;
    if (navigator.mediaDevices) {
      navigator.mediaDevices.getUserMedia = async () => {
        (window as any).cameraRequests++;
        throw new Error("No camera acquisition in this software journey");
      };
    }
  });
  await enterGuest(page);
  await acknowledgeNotice(page);
  await page.getByTestId("review-context").click();
  await page
    .getByRole("switch", { name: "I have reviewed this check’s context." })
    .check();
  await page.getByTestId("start-check").click();
  await page.getByRole("button", { name: "3 Saliva", exact: true }).click();
  await page.getByTestId("simulate-saliva").click();
  const identity = await page.getByText(/Check 3 of 8 ·/).textContent();
  await expect(page.getByTestId("simulate-saliva")).toBeDisabled();
  await page.getByRole("tab", { name: "Settings", exact: true }).click();
  await expect(
    page.getByText("Browser permission is checked at eye preview", {
      exact: true,
    }),
  ).toBeVisible();
  await page
    .getByRole("button", { name: "Refresh permission status", exact: true })
    .click();
  await page.getByRole("tab", { name: "Check", exact: true }).click();
  await expect(page.getByText(identity!, { exact: true })).toBeVisible();
  await expect(page.getByTestId("simulate-saliva")).toBeDisabled();
  await page.getByRole("button", { name: "‹ Back", exact: true }).click();
  await page
    .getByRole("button", { name: "Keep draft and leave", exact: true })
    .click();
  await page.getByRole("tab", { name: "Check", exact: true }).click();
  await expect(page.getByText(identity!, { exact: true })).toBeVisible();
  await expect(page.getByTestId("simulate-saliva")).toBeDisabled();
  expect(await page.evaluate(() => (window as any).cameraRequests)).toBe(0);
});
