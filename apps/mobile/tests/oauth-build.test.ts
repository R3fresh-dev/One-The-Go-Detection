import test from "node:test";
import assert from "node:assert/strict";
import configure from "../app.config";

test("cloud builds require independent hosted origin and exact web callback pins", () => {
  const keys = [
    "APP_ENV",
    "EXPO_PUBLIC_APP_ENV",
    "EXPO_PUBLIC_HOSTED_PREVIEW",
    "EXPO_PUBLIC_SERVERLESS",
    "EXPO_PUBLIC_API_URL",
    "EXPO_PUBLIC_OAUTH_ISSUER",
    "EXPO_PUBLIC_OAUTH_CLIENT_ID",
    "EXPO_PUBLIC_OAUTH_ORIGIN",
    "EXPO_PUBLIC_OAUTH_WEB_CALLBACK_URI",
  ];
  const saved = Object.fromEntries(keys.map((key) => [key, process.env[key]]));
  try {
    process.env.EXPO_PUBLIC_HOSTED_PREVIEW = "false";
    process.env.EXPO_PUBLIC_SERVERLESS = "false";
    process.env.EXPO_PUBLIC_API_URL = "https://api.owned-research.org";
    process.env.EXPO_PUBLIC_OAUTH_ISSUER =
      "https://cognito-idp.us-east-2.amazonaws.com/us-east-2_pool";
    process.env.EXPO_PUBLIC_OAUTH_CLIENT_ID = "actual-public-client";
    for (const environment of ["qa", "prod"]) {
      process.env.APP_ENV = process.env.EXPO_PUBLIC_APP_ENV = environment;
      delete process.env.EXPO_PUBLIC_OAUTH_ORIGIN;
      delete process.env.EXPO_PUBLIC_OAUTH_WEB_CALLBACK_URI;
      assert.throws(
        () => configure({ config: {} } as any),
        /authentication|origin|configured/i,
      );
      process.env.EXPO_PUBLIC_OAUTH_ORIGIN =
        "https://admitted.auth.us-east-2.amazoncognito.com";
      assert.throws(
        () => configure({ config: {} } as any),
        /callback|configured/i,
      );
      process.env.EXPO_PUBLIC_OAUTH_WEB_CALLBACK_URI =
        "https://web.owned-research.org/";
      const built = configure({ config: {} } as any).extra!;
      assert.equal(built.oauthOrigin, process.env.EXPO_PUBLIC_OAUTH_ORIGIN);
      assert.equal(
        built.webCallbackUri,
        process.env.EXPO_PUBLIC_OAUTH_WEB_CALLBACK_URI,
      );
      assert.deepEqual(built.redirectUris, [
        `otgd${environment === "qa" ? "-qa" : ""}://oauth/callback`,
        "https://web.owned-research.org/",
      ]);
      for (const bad of [
        "https://admitted.auth.us-east-2.amazoncognito.com/path",
        "https://admitted.auth.us-east-2.amazoncognito.com?x=1",
        "https://user@admitted.auth.us-east-2.amazoncognito.com",
        "https://admitted.auth.us-east-2.amazoncognito.com:443",
        "http://admitted.auth.us-east-2.amazoncognito.com",
      ]) {
        process.env.EXPO_PUBLIC_OAUTH_ORIGIN = bad;
        assert.throws(
          () => configure({ config: {} } as any),
          /authentication|origin/i,
        );
      }
      process.env.EXPO_PUBLIC_OAUTH_ORIGIN =
        "https://admitted.auth.us-east-2.amazoncognito.com";
      for (const bad of [
        "https://web.owned-research.org/callback",
        "https://web.owned-research.org/#x",
        "https://web.owned-research.org/?x=1",
        "https://user@web.owned-research.org/",
        "http://web.owned-research.org/",
      ]) {
        process.env.EXPO_PUBLIC_OAUTH_WEB_CALLBACK_URI = bad;
        assert.throws(() => configure({ config: {} } as any), /callback/i);
      }
    }
  } finally {
    for (const key of keys) {
      if (saved[key] === undefined) delete process.env[key];
      else process.env[key] = saved[key];
    }
  }
});
