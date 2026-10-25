import { defineConfig, devices } from "@playwright/test";
export default defineConfig({
  testDir: "./e2e",
  testMatch: "authenticated-live.spec.ts",
  timeout: 240_000,
  expect: { timeout: 15_000 },
  retries: 0,
  workers: 1,
  reporter: [
    ["list"],
    ["html", { open: "never", outputFolder: "playwright-live-report" }],
  ],
  outputDir: "test-results-live",
  use: {
    baseURL: "http://localhost:8082",
    // OAuth codes and bearer credentials must not enter traces or HAR files.
    trace: "off",
    screenshot: "off",
    video: "off",
    launchOptions: process.env.OTGD_CHROMIUM_PATH
      ? {
          executablePath: process.env.OTGD_CHROMIUM_PATH,
          args: ["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu"],
        }
      : undefined,
  },
  projects: [
    {
      name: "live-mobile",
      use: { ...devices["Pixel 7"], browserName: "chromium" },
    },
    {
      name: "live-desktop",
      use: { viewport: { width: 1440, height: 1000 }, browserName: "chromium" },
    },
  ],
  webServer: {
    command: "OTGD_WEB_DIST=dist OTGD_WEB_PORT=8082 node scripts/serve-web.mjs",
    url: "http://localhost:8082",
    reuseExistingServer: false,
    timeout: 20_000,
  },
});
