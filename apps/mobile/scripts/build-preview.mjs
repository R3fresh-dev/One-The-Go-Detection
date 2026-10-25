import { spawnSync } from "node:child_process";
import { mkdirSync, writeFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const output = resolve(root, "dist-preview");
const result = spawnSync(
  process.execPath,
  [
    resolve(root, "node_modules/expo/bin/cli"),
    "export",
    "--platform",
    "web",
    "--clear",
    "--output-dir",
    output,
  ],
  {
    cwd: root,
    stdio: "inherit",
    env: {
      ...process.env,
      APP_ENV: "local",
      EXPO_PUBLIC_APP_ENV: "local",
      EXPO_PUBLIC_HOSTED_PREVIEW: "true",
      EXPO_NO_TELEMETRY: "1",
      EXPO_NO_DOTENV: "1",
      EXPO_PUBLIC_API_URL: "https://unavailable.invalid",
      EXPO_PUBLIC_OAUTH_ISSUER: "https://unavailable.invalid",
      EXPO_PUBLIC_OAUTH_ORIGIN: "https://unavailable.invalid",
      EXPO_PUBLIC_OAUTH_WEB_CALLBACK_URI: "https://unavailable.invalid/",
      EXPO_PUBLIC_OAUTH_CLIENT_ID: "otgd-hosted-fictional",
    },
  },
);
if (result.error) throw result.error;
if (result.status !== 0) process.exit(result.status ?? 1);
mkdirSync(output, { recursive: true });
writeFileSync(
  resolve(output, "preview-manifest.json"),
  JSON.stringify(
    {
      schema_version: "1.0.0",
      built_at: new Date().toISOString(),
      environment: "local",
      fictional_guest_only: true,
      account_services: false,
      sensor_permissions: false,
      raw_recording: false,
      uploads: false,
      persistence: "browser_memory_only",
      inference_available: false,
      build_environment: {
        APP_ENV: "local",
        EXPO_PUBLIC_APP_ENV: "local",
        EXPO_PUBLIC_HOSTED_PREVIEW: "true",
        EXPO_NO_DOTENV: "1",
        EXPO_PUBLIC_API_URL: "https://unavailable.invalid",
        EXPO_PUBLIC_OAUTH_ISSUER: "https://unavailable.invalid",
        EXPO_PUBLIC_OAUTH_ORIGIN: "https://unavailable.invalid",
        EXPO_PUBLIC_OAUTH_WEB_CALLBACK_URI: "https://unavailable.invalid/",
        EXPO_PUBLIC_OAUTH_CLIENT_ID: "otgd-hosted-fictional",
      },
    },
    null,
    2,
  ) + "\n",
);
