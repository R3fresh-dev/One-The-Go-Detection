import { test, expect, type Page } from "@playwright/test";
import { buildSync } from "esbuild";
import { resolve } from "node:path";
import { preparationConfiguration } from "./fixtures/preparation-configuration";

const preparationBundle = buildSync({
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
}).outputFiles![0]!.text;
const preparationPages = new WeakSet<Page>();
async function preparationDOM(page: Page, rest = 30) {
  if (!preparationPages.has(page)) {
    await page.clock.install({ time: Date.parse("2026-10-11T12:00:00Z") });
    preparationPages.add(page);
  } else await page.clock.setSystemTime(Date.parse("2026-10-11T12:00:00Z"));
  await page.goto("/");
  await page.setContent('<main id="root"></main>');
  await page.addScriptTag({ content: preparationBundle });
  const configuration = preparationConfiguration(rest);
  await page.evaluate(
    (value) => (window as any).renderPreparation(value),
    configuration,
  );
  await page
    .getByRole("radio", { name: "Fictional portable bench", exact: true })
    .click();
  return configuration;
}

test("preparation wall-clock forward/backward discontinuity clears guidance and declarations until a fresh admitted rest", async ({
  page,
}) => {
  for (const shift of [7_200_000, -7_200_000]) {
    const configuration = await preparationDOM(page);
    await page
      .getByRole("button", { name: "Start approved rest period", exact: true })
      .click();
    await page.evaluate(() => (window as any).resolvePreparation());
    await expect(
      page.getByText("Required foreground rest: 30 seconds remaining.", {
        exact: true,
      }),
    ).toBeVisible();
    await page
      .getByRole("switch", { name: "posture_confirmed", exact: true })
      .check();
    const before = await page.evaluate(() => Date.now());
    await page.clock.setSystemTime(before + shift);
    await page.clock.runFor(200);
    await expect(page.getByText(/Preparation timing changed/)).toBeVisible();
    await expect(
      page.getByText(/Begin only after the service saves/),
    ).toBeVisible();
    for (const item of configuration.participant_protocol
      .required_confirmations)
      await expect(
        page.getByRole("switch", { name: item.text, exact: true }),
      ).not.toBeChecked();
    const start = page.getByRole("button", {
      name: "Start authorized pulse capture",
      exact: true,
    });
    await expect(start).toBeDisabled();
    expect(
      (await page.evaluate(() => (window as any).participantCalls)).map(
        (call: any) => call.kind,
      ),
    ).toEqual(["prepare", "stop"]);
    await page.clock.fastForward(60_000);
    await expect(start).toBeDisabled();
    await page
      .getByRole("button", { name: "Start approved rest period", exact: true })
      .click();
    await page.evaluate(() => (window as any).resolvePreparation());
    await page.clock.fastForward(30_000);
    for (const item of configuration.participant_protocol
      .required_confirmations)
      await page.getByRole("switch", { name: item.text, exact: true }).check();
    await expect(start).toBeEnabled();
    await start.click();
    expect(
      (await page.evaluate(() => (window as any).participantCalls)).map(
        (call: any) => call.kind,
      ),
    ).toEqual(["prepare", "stop", "prepare", "capture"]);
  }
});

test("a wall-clock jump between rest completion and Start immediately clears authority without a capture", async ({
  page,
}) => {
  const configuration = await preparationDOM(page, 0);
  await page
    .getByRole("button", { name: "Start approved rest period", exact: true })
    .click();
  await page.evaluate(() => (window as any).resolvePreparation());
  for (const item of configuration.participant_protocol.required_confirmations)
    await page.getByRole("switch", { name: item.text, exact: true }).check();
  const start = page.getByRole("button", {
    name: "Start authorized pulse capture",
    exact: true,
  });
  await expect(start).toBeEnabled();
  const now = await page.evaluate(() => Date.now());
  await page.clock.pauseAt(now + 1000);
  await page.clock.setSystemTime(now + 3_600_000);
  // Timers stay paused so the actual explicit Start handler must perform the guard.
  await start.click({ force: true });
  await expect(start).toBeDisabled();
  await expect(page.getByText(/Preparation timing changed/)).toBeVisible();
  for (const item of configuration.participant_protocol.required_confirmations)
    await expect(
      page.getByRole("switch", { name: item.text, exact: true }),
    ).not.toBeChecked();
  expect(
    (await page.evaluate(() => (window as any).participantCalls)).map(
      (call: any) => call.kind,
    ),
  ).toEqual(["prepare", "stop"]);
});

test("zero and maximum approved rest retain explicit declarations and unshortened monotonic bounds", async ({
  page,
}) => {
  for (const rest of [0, 3600]) {
    const configuration = await preparationDOM(page, rest);
    await page
      .getByRole("button", { name: "Start approved rest period", exact: true })
      .click();
    await page.evaluate(() => (window as any).resolvePreparation());
    const start = page.getByRole("button", {
      name: "Start authorized pulse capture",
      exact: true,
    });
    await expect(start).toBeDisabled();
    if (rest) {
      await page.clock.fastForward(rest * 1000 - 1000);
      await expect(
        page.getByRole("switch", { name: "rest_completed", exact: true }),
      ).toBeDisabled();
      await page.clock.fastForward(1000);
    }
    for (const item of configuration.participant_protocol
      .required_confirmations)
      await page.getByRole("switch", { name: item.text, exact: true }).check();
    await expect(start).toBeEnabled();
    await start.click();
    expect(
      (await page.evaluate(() => (window as any).participantCalls)).map(
        (call: any) => call.kind,
      ),
    ).toEqual(["prepare", "capture"]);
  }
});

test("an unavailable wall clock after admitted preparation stops its attempt instead of leaving it armed", async ({
  page,
}) => {
  await preparationDOM(page, 0);
  await page
    .getByRole("button", { name: "Start approved rest period", exact: true })
    .click();
  await page.evaluate(() => {
    Date.now = () => NaN;
    (window as any).resolvePreparation();
  });
  await expect(
    page.getByText(
      "Valid monotonic and wall preparation clocks are required.",
      { exact: true },
    ),
  ).toBeVisible();
  await expect(
    page.getByRole("button", {
      name: "Start authorized pulse capture",
      exact: true,
    }),
  ).toBeDisabled();
  expect(
    (await page.evaluate(() => (window as any).participantCalls)).map(
      (call: any) => call.kind,
    ),
  ).toEqual(["prepare", "stop"]);
});

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

// Review corrections exercised against the exported production DOM.
test("route headings receive focus across tabs, deeper navigation and Back", async ({
  page,
}) => {
  await enterGuest(page);
  await acknowledgeNotice(page);
  await expect(
    page.getByRole("heading", { name: "A check with context", exact: true }),
  ).toBeFocused();
  await page.getByRole("tab", { name: "Settings", exact: true }).click();
  await expect(
    page.getByRole("heading", { name: "Settings", exact: true }),
  ).toBeFocused();
  await openPrivacy(page);
  await expect(
    page.getByRole("heading", { name: "Privacy & data", exact: true }),
  ).toBeFocused();
  await page
    .getByRole("button", { name: "Clear local records", exact: true })
    .click();
  await expect(
    page.getByRole("heading", {
      name: "Clear this workspace’s local records?",
      exact: true,
    }),
  ).toBeFocused();
  await page.getByRole("button", { name: "Cancel", exact: true }).click();
  await expect(
    page.getByRole("button", { name: "Clear local records", exact: true }),
  ).toBeFocused();
  await page.getByRole("button", { name: "‹ Back", exact: true }).click();
  await expect(
    page.getByRole("heading", { name: "Settings", exact: true }),
  ).toBeFocused();
  await page.getByRole("tab", { name: "History", exact: true }).click();
  await expect(
    page.getByRole("heading", { name: "Your check history", exact: true }),
  ).toBeFocused();
});
async function modalAnimationSeconds(page: Page) {
  return page
    .getByRole("dialog", {
      name: "Clear this workspace’s local records?",
      exact: true,
    })
    .evaluate((dialog) => {
      let maximum = 0;
      for (
        let node: HTMLElement | null = dialog as HTMLElement;
        node;
        node = node.parentElement
      ) {
        const style = getComputedStyle(node);
        if (style.animationName !== "none")
          maximum = Math.max(
            maximum,
            ...style.animationDuration
              .split(",")
              .map(
                (duration) =>
                  parseFloat(duration) *
                  (duration.trim().endsWith("ms") ? 0.001 : 1),
              ),
          );
      }
      return maximum;
    });
}
test("system motion and explicit overrides control rendered ordinary modal animation", async ({
  page,
}) => {
  await page.emulateMedia({ reducedMotion: "reduce" });
  await enterGuest(page);
  await acknowledgeNotice(page);
  await page.getByRole("tab", { name: "Settings", exact: true }).click();
  const motion = page.getByRole("switch", {
    name: "Reduce motion",
    exact: true,
  });
  await expect(motion).toBeChecked();
  await openPrivacy(page);
  await page
    .getByRole("button", { name: "Clear local records", exact: true })
    .click();
  await expect.poll(() => modalAnimationSeconds(page)).toBe(0);
  await page.getByRole("button", { name: "Cancel", exact: true }).click();
  await page.getByRole("tab", { name: "Settings", exact: true }).click();
  await motion.uncheck();
  await openPrivacy(page);
  await page
    .getByRole("button", { name: "Clear local records", exact: true })
    .click();
  await expect.poll(() => modalAnimationSeconds(page)).toBeGreaterThan(0);
  await page.getByRole("button", { name: "Cancel", exact: true }).click();
  await page.getByRole("tab", { name: "Settings", exact: true }).click();
  await expect(motion).not.toBeChecked();
  await motion.check();
  await page.emulateMedia({ reducedMotion: "no-preference" });
  await expect(motion).toBeChecked();
  await openPrivacy(page);
  await page
    .getByRole("button", { name: "Clear local records", exact: true })
    .click();
  await expect.poll(() => modalAnimationSeconds(page)).toBe(0);
  await page.getByRole("button", { name: "Cancel", exact: true }).click();
  await page.getByRole("tab", { name: "Settings", exact: true }).click();
  await page
    .getByRole("button", { name: "Use system motion setting", exact: true })
    .click();
  await expect(motion).not.toBeChecked();
  await page.emulateMedia({ reducedMotion: "reduce" });
  await expect(motion).toBeChecked();
});
test("rendered destructive labels meet contrast minimum in light and dark themes", async ({
  page,
}, testInfo) => {
  await enterGuest(page);
  await acknowledgeNotice(page);
  const observations: unknown[] = [];
  const luminance = (channels: number[]) => {
    const linear = channels.map((value) => {
      value /= 255;
      return value <= 0.04045
        ? value / 12.92
        : ((value + 0.055) / 1.055) ** 2.4;
    });
    return linear[0]! * 0.2126 + linear[1]! * 0.7152 + linear[2]! * 0.0722;
  };
  const rgb = (color: string) =>
    color
      .match(/[\d.]+/g)!
      .slice(0, 3)
      .map(Number);
  for (const theme of ["Light", "Dark"]) {
    await page.getByRole("tab", { name: "Settings", exact: true }).click();
    await page.getByRole("radio", { name: theme, exact: true }).click();
    await openPrivacy(page);
    await page
      .getByRole("button", { name: "Clear local records", exact: true })
      .click();
    const button = page
      .getByRole("dialog")
      .getByRole("button", { name: "Clear local records", exact: true });
    for (const state of ["normal", "pressed"]) {
      if (state === "pressed") {
        const box = (await button.boundingBox())!;
        await page.mouse.move(box.x + box.width / 2, box.y + box.height / 2);
        await page.mouse.down();
        await expect
          .poll(() =>
            button.evaluate((element) =>
              Number(getComputedStyle(element).opacity),
            ),
          )
          .toBeLessThan(1);
      }
      const colors = await button.evaluate((element) => ({
        foreground: getComputedStyle(element.firstElementChild!).color,
        background: getComputedStyle(element).backgroundColor,
        surface: getComputedStyle(element.parentElement!).backgroundColor,
        opacity: Number(getComputedStyle(element).opacity),
      }));
      const composite = (color: string) =>
        rgb(color).map(
          (value, index) =>
            value * colors.opacity +
            rgb(colors.surface)[index]! * (1 - colors.opacity),
        );
      const values = [
        luminance(composite(colors.foreground)),
        luminance(composite(colors.background)),
      ].sort((a, b) => b - a);
      const contrast = (values[0]! + 0.05) / (values[1]! + 0.05);
      observations.push({ theme, state, ...colors, contrast });
      if (state === "pressed") {
        // Release outside the control so the test does not confirm deletion.
        await page.mouse.move(0, 0);
        await page.mouse.up();
      }
      expect(
        contrast,
        `${theme}/${state}: ${JSON.stringify(colors)}`,
      ).toBeGreaterThanOrEqual(4.5);
    }
    await expect(
      page
        .getByRole("dialog")
        .getByRole("button", { name: "Cancel", exact: true }),
    ).toBeEnabled();
    await page.getByRole("button", { name: "Cancel", exact: true }).click();
  }
  await testInfo.attach("computed-destructive-contrast.json", {
    body: JSON.stringify(observations, null, 2),
    contentType: "application/json",
  });
});
