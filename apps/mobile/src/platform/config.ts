import Constants from "expo-constants";
import type { Environment } from "../core/types";
import { IntegrityError } from "../core/integrity";
const extra = Constants.expoConfig?.extra ?? {};
export const BUILD = Object.freeze({
  environment: (extra.environment ?? "local") as Environment,
  apiUrl: String(extra.apiUrl ?? "http://localhost:8000").replace(/\/$/, ""),
  issuer: String(extra.issuer ?? "http://localhost:8081").replace(/\/$/, ""),
  clientId: String(extra.clientId ?? "otgd-local-mobile"),
  redirectUri: String(extra.redirectUri ?? "otgd-local://oauth/callback"),
  version:
    Constants.nativeAppVersion ?? Constants.expoConfig?.version ?? "0.2.0",
  buildNumber: Constants.nativeBuildVersion ?? String(extra.buildNumber ?? "1"),
  contract: "1.0.0 / scientific 0.1.0",
});
export function validateBuild(): void {
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
