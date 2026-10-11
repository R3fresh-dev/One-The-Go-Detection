import { randomUUID } from "node:crypto";
import configFixture from "../../testfixtures/backend-app-config.json";
import capabilitiesFixture from "../../testfixtures/backend-capabilities.json";
import { clone, digestText } from "../../src/core/integrity";
export function deferred<T>() {
  let resolve!: (value: T) => void;
  let reject!: (error: unknown) => void;
  const promise = new Promise<T>((a, b) => {
    resolve = a;
    reject = b;
  });
  return { promise, resolve, reject };
}
export function customerService() {
  const text = "Fictional account notice for controller unit tests.",
    config: any = clone(configFixture),
    caps: any = clone(capabilitiesFixture);
  config.notice.sha256 = digestText(text);
  caps.notice.sha256 = config.notice.sha256;
  caps.account_ref = randomUUID();
  let profile: any = {
    profile_version_id: null,
    revision: 0,
    profile: null,
    history: null,
    context: null,
  };
  const calls: { path: string; method: string; body: any; headers: Headers }[] =
    [];
  const overrides = new Map<
    string,
    (call: (typeof calls)[number]) => Promise<Response> | Response
  >();
  const notice = {
    version: "v1",
    locale: "en",
    content_type: "text/plain",
    text,
    sha256: config.notice.sha256,
    mandatory: true,
  };
  const result = (
    value: unknown,
    status = 200,
    headers: Record<string, string> = {},
  ) =>
    new Response(JSON.stringify(value), {
      status,
      headers: { "Content-Type": "application/json", ...headers },
    });
  const fetcher: typeof fetch = async (input, init) => {
    const url = new URL(String(input)),
      raw = String(init?.body || "");
    const call = {
      path: url.pathname + url.search,
      method: init?.method || "GET",
      body: raw
        ? raw.startsWith("{")
          ? JSON.parse(raw)
          : Object.fromEntries(new URLSearchParams(raw))
        : null,
      headers: new Headers(init?.headers),
    };
    calls.push(call);
    const override =
      overrides.get(call.method + " " + call.path) || overrides.get(call.path);
    if (override) return override(call);
    if (url.pathname === "/oauth2/token")
      return result({
        access_token: "signed-unit-access",
        refresh_token: "unit-refresh",
        token_type: "Bearer",
        expires_in: 900,
      });
    if (url.pathname === "/oauth2/revoke" || url.pathname === "/v1/auth/logout")
      return result({ state: "revoked" });
    if (url.pathname === "/v1/app-config") return result(config);
    if (url.pathname === "/v1/me/capabilities") return result(caps);
    if (url.pathname === "/v1/notices/v1") return result(notice);
    if (url.pathname === "/v1/me/profile") {
      if (call.method === "PATCH")
        profile = {
          ...call.body,
          profile_version_id: randomUUID(),
          revision: profile.revision + 1,
        };
      return result(profile, 200, { ETag: '"' + profile.revision + '"' });
    }
    if (url.pathname === "/v1/me/acknowledgments") {
      caps.notice.acknowledged = true;
      return result({ version: "v1", sha256: config.notice.sha256 });
    }
    if (url.pathname === "/v1/me/studies") return result({ items: [] });
    if (url.pathname === "/v1/sessions" && call.method === "GET")
      return result({ items: [], next_cursor: null });
    return result({ code: "UNIT_ROUTE_UNCONFIGURED", message: call.path }, 404);
  };
  return {
    config,
    caps,
    calls,
    overrides,
    notice,
    result,
    fetcher,
    getProfile: () => profile,
    setProfile: (value: any) => {
      profile = value;
    },
  };
}
