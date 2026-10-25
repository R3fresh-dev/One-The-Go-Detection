import {
  validateOAuthPolicy as validateBuildPolicy,
  type OAuthPolicy,
} from "../../oauth-build-policy.js";
export type { OAuthPolicy } from "../../oauth-build-policy.js";
import { IntegrityError, knownKeys, requireObject } from "./integrity";
import type { AppConfig } from "./types";

const paths = {
  authorization_endpoint: "/oauth2/authorize",
  token_endpoint: "/oauth2/token",
  revocation_endpoint: "/oauth2/revoke",
  logout_endpoint: "/logout",
} as const;
function refuse(code: string, message: string): never {
  throw new IntegrityError(code, message);
}
export function validateOAuthPolicy(policy: OAuthPolicy): void {
  try {
    validateBuildPolicy(policy);
  } catch (error) {
    throw new IntegrityError(
      (error as { code: string }).code,
      (error as Error).message,
    );
  }
}

/** Return an independent admitted snapshot so later caller mutation cannot redirect traffic. */
export function admitOAuthMetadata(
  value: unknown,
  policy: OAuthPolicy,
): AppConfig["auth"] {
  validateOAuthPolicy(policy);
  const auth = requireObject(value);
  knownKeys(auth, [
    "issuer",
    "client_id",
    ...Object.keys(paths),
    "redirect_uris",
  ]);
  if (auth.issuer !== policy.issuer || auth.client_id !== policy.clientId)
    refuse(
      "AUTH_CONFIG_MISMATCH",
      "The authentication identity differs from this build.",
    );
  for (const [key, path] of Object.entries(paths)) {
    const endpoint = auth[key];
    if (
      (key === "revocation_endpoint" || key === "logout_endpoint") &&
      endpoint === undefined
    )
      continue;
    if (endpoint !== policy.oauthOrigin + path)
      refuse(
        "AUTH_ENDPOINT_INVALID",
        "An authentication endpoint differs from this build's admitted endpoint.",
      );
  }
  if (
    !Array.isArray(auth.redirect_uris) ||
    auth.redirect_uris.length !== policy.redirectUris.length ||
    new Set(auth.redirect_uris).size !== auth.redirect_uris.length ||
    auth.redirect_uris.some(
      (uri) => typeof uri !== "string" || !policy.redirectUris.includes(uri),
    )
  )
    refuse(
      "AUTH_CALLBACK_INVALID",
      "The authentication callbacks differ from this build.",
    );
  return {
    issuer: policy.issuer,
    client_id: policy.clientId,
    authorization_endpoint: String(auth.authorization_endpoint),
    token_endpoint: String(auth.token_endpoint),
    ...(auth.revocation_endpoint === undefined
      ? {}
      : { revocation_endpoint: String(auth.revocation_endpoint) }),
    ...(auth.logout_endpoint === undefined
      ? {}
      : { logout_endpoint: String(auth.logout_endpoint) }),
    redirect_uris: [...policy.redirectUris],
  };
}
export function admitOAuthCallback(
  callback: string,
  policy: OAuthPolicy,
): void {
  validateOAuthPolicy(policy);
  if (!policy.redirectUris.includes(callback))
    refuse(
      "AUTH_CALLBACK_INVALID",
      "The authentication callback differs from this build.",
    );
}
export function admitProviderLogoutUrl(
  value: string,
  callback: string,
  policy: OAuthPolicy,
): void {
  admitOAuthCallback(callback, policy);
  const expected = new URL(policy.oauthOrigin + paths.logout_endpoint);
  expected.searchParams.set("client_id", policy.clientId);
  expected.searchParams.set("logout_uri", callback);
  if (value !== expected.toString())
    refuse(
      "AUTH_ENDPOINT_INVALID",
      "The authentication logout endpoint differs from this build.",
    );
}
