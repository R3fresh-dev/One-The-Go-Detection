import { test, expect } from "@playwright/test";

test("standalone fictional guest UI saves a check with zero account, upload, camera or Bluetooth calls and reload clears browser records", async ({
  page,
}) => {
  const external: string[] = [];
  page.on("request", (request) => {
    if (
      !request.url().startsWith("http://127.0.0.1:8083/") &&
      !request.url().startsWith("data:")
    )
      external.push(request.url());
  });
  await page.addInitScript(() => {
    (window as any).sensorCalls = [];
    if (navigator.mediaDevices)
      (navigator.mediaDevices as any).getUserMedia = () => {
        (window as any).sensorCalls.push("camera");
        throw Error("Hosted preview must not request camera");
      };
    Object.defineProperty(navigator, "bluetooth", {
      configurable: true,
      value: {
        requestDevice: () => {
          (window as any).sensorCalls.push("bluetooth");
          throw Error("Hosted preview must not request Bluetooth");
        },
      },
    });
  });
  await page.goto("/");
  await expect(page.getByTestId("fictional-preview-banner")).toBeVisible();
  await expect(page.getByTestId("sign-in")).toHaveCount(0);
  await page.getByTestId("explore-demo").click();
  await page.getByRole("button", { name: "Start demo", exact: true }).click();
  await page
    .getByRole("switch", {
      name: "I have read how this app handles data.",
      exact: true,
    })
    .check();
  await page.getByTestId("acknowledge-notice").click();
  await page.getByTestId("review-context").click();
  await page
    .getByRole("switch", {
      name: "I have reviewed this check’s context.",
      exact: true,
    })
    .check();
  await page.getByTestId("start-check").click();
  await page.getByRole("button", { name: "5 Pulse", exact: true }).click();
  await expect(
    page.getByRole("button", { name: /capture|record|Start task/i }),
  ).toHaveCount(0);
  await page.getByRole("button", { name: "8 Review", exact: true }).click();
  await page.getByTestId("save-check").click();
  await expect(
    page.getByRole("heading", { name: "Measurements saved", exact: true }),
  ).toBeVisible();
  await expect(page.getByTestId("upload-check")).toHaveCount(0);
  await page.getByRole("tab", { name: "History", exact: true }).click();
  await expect(
    page.getByRole("heading", { name: "Your check history", exact: true }),
  ).toBeVisible();
  await page.reload();
  await expect(page.getByTestId("explore-demo")).toBeVisible();
  await expect(page.getByTestId("resume-check")).toHaveCount(0);
  expect(external).toEqual([]);
  expect(await page.evaluate(() => (window as any).sensorCalls)).toEqual([]);
});
