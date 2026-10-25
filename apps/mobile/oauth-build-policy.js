// Shared public build admission. Plain JavaScript is required by Expo's config loader.
function refuse(code, message) {
  const error = new Error(message);
  error.code = code;
  throw error;
}
function parsed(value, code, message) {
  if (typeof value !== "string" || !value || value.length > 2048)
    return refuse(code, message);
  try {
    return new URL(value);
  } catch {
    return refuse(code, message);
  }
}
function validateOAuthPolicy(policy) {
  const cloud = ["qa", "prod"].includes(policy.environment);
  const origin = parsed(
    policy.oauthOrigin,
    "AUTH_ORIGIN_INVALID",
    "The authentication origin is not configured for this build.",
  );
  if (
    !["http:", "https:"].includes(origin.protocol) ||
    (cloud && origin.protocol !== "https:") ||
    origin.origin !== policy.oauthOrigin ||
    origin.username ||
    origin.password ||
    origin.search ||
    origin.hash ||
    origin.pathname !== "/"
  )
    refuse(
      "AUTH_ORIGIN_INVALID",
      "The authentication origin must be an exact configured origin.",
    );
  const issuer = parsed(
    policy.issuer,
    "AUTH_CONFIG_MISMATCH",
    "The authentication issuer is not configured for this build.",
  );
  if (
    !["http:", "https:"].includes(issuer.protocol) ||
    (cloud && issuer.protocol !== "https:") ||
    issuer.username ||
    issuer.password ||
    issuer.search ||
    issuer.hash ||
    policy.issuer !==
      (issuer.pathname === "/"
        ? issuer.origin
        : issuer.origin + issuer.pathname) ||
    typeof policy.clientId !== "string" ||
    !policy.clientId
  )
    refuse("AUTH_CONFIG_MISMATCH", "The authentication identity is invalid.");
  if (
    !Array.isArray(policy.redirectUris) ||
    policy.redirectUris.length !== 2 ||
    new Set(policy.redirectUris).size !== 2
  )
    refuse(
      "AUTH_CALLBACK_INVALID",
      "The authentication callbacks are not configured for this build.",
    );
  const native =
    policy.environment === "prod"
      ? "otgd://oauth/callback"
      : `otgd-${policy.environment === "test" ? "local" : policy.environment}://oauth/callback`;
  const nativeUris = policy.redirectUris.filter(
    (uri) =>
      uri === native ||
      (policy.environment === "test" && uri === "otgd-test://oauth/callback"),
  );
  if (nativeUris.length !== 1)
    refuse(
      "AUTH_CALLBACK_INVALID",
      "The authentication native callback differs from this build.",
    );
  const web = policy.redirectUris.find((uri) => !nativeUris.includes(uri));
  const callback = parsed(
    web,
    "AUTH_CALLBACK_INVALID",
    "The authentication web callback is not configured for this build.",
  );
  if (
    !["http:", "https:"].includes(callback.protocol) ||
    (cloud && callback.protocol !== "https:") ||
    callback.username ||
    callback.password ||
    callback.origin + "/" !== web
  )
    refuse(
      "AUTH_CALLBACK_INVALID",
      "The authentication web callback must be an exact configured root callback.",
    );
}

module.exports = { validateOAuthPolicy };
