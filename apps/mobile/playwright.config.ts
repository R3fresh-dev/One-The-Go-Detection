import { defineConfig, devices } from "@playwright/test";
export default defineConfig({
  testDir: "./e2e",
  timeout: 60_000,
  retries: 0,
  workers: 1,
  reporter: [
    ["list"],
    ["html", { open: "never", outputFolder: "playwright-report" }],
  ],
  use: {
    baseURL: "http://localhost:8082",
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
    launchOptions: process.env.OTGD_CHROMIUM_PATH
      ? {
          executablePath: process.env.OTGD_CHROMIUM_PATH,
          args: ["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu"],
        }
      : undefined,
  },
  projects: [
    {
      name: "mobile-web-preview",
      use: { ...devices["Pixel 7"], browserName: "chromium" },
    },
    {
      name: "desktop-web-preview",
      use: { viewport: { width: 1440, height: 1000 }, browserName: "chromium" },
    },
  ],
  webServer: {
    command: "node scripts/serve-web.mjs",
    url: "http://localhost:8082",
    reuseExistingServer: !process.env.CI,
    timeout: 20_000,
  },
});
