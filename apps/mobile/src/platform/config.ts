import Constants from "expo-constants";
import type { Environment } from "../core/types";
import { IntegrityError } from "../core/integrity";
const extra = Constants.expoConfig?.extra ?? {};
export const BUILD = Object.freeze({
  environment: (extra.environment ??
    process.env.EXPO_PUBLIC_APP_ENV ??
    "local") as Environment,
  hostedPreview:
    extra.hostedPreview === true ||
    process.env.EXPO_PUBLIC_HOSTED_PREVIEW === "true",
  apiUrl: String(
    extra.apiUrl ?? process.env.EXPO_PUBLIC_API_URL ?? "http://localhost:8000",
  ).replace(/\/$/, ""),
  issuer: String(
    extra.issuer ??
      process.env.EXPO_PUBLIC_OAUTH_ISSUER ??
      "http://localhost:8081",
  ).replace(/\/$/, ""),
  clientId: String(
    extra.clientId ??
      process.env.EXPO_PUBLIC_OAUTH_CLIENT_ID ??
      "otgd-local-mobile",
  ),
  redirectUri: String(extra.redirectUri ?? "otgd-local://oauth/callback"),
  version:
    Constants.nativeAppVersion ?? Constants.expoConfig?.version ?? "0.2.0",
  buildNumber: Constants.nativeBuildVersion ?? String(extra.buildNumber ?? "1"),
  contract: "1.0.0 / scientific 0.1.0",
});
export function validateBuild(): void {
  if (BUILD.hostedPreview && BUILD.environment !== "local")
    throw new IntegrityError(
      "PREVIEW_ENVIRONMENT_INVALID",
      "The fictional preview cannot run in QA or production.",
    );
  if (!["local", "qa", "prod", "test"].includes(BUILD.environment))
    throw new IntegrityError(
      "ENVIRONMENT_INVALID",
      "This build has an unsupported environment.",
    );
  if (
    ["qa", "prod"].includes(BUILD.environment) &&
    (!BUILD.apiUrl.startsWith("https://") ||
      !BUILD.issuer.startsWith("https://") ||
      /local|example|placeholder/i.test(BUILD.clientId))
  )
    throw new IntegrityError(
      "ENVIRONMENT_INVALID",
      "This build is missing its configured secure service identity.",
    );
}
