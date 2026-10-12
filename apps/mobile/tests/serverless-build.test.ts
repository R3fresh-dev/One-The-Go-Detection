import test from "node:test";
import assert from "node:assert/strict";
import configure from "../app.config";

test("longer service deadlines are an explicit cloud build setting", () => {
  const keys = [
    "APP_ENV",
    "EXPO_PUBLIC_APP_ENV",
    "EXPO_PUBLIC_SERVERLESS",
    "EXPO_PUBLIC_HOSTED_PREVIEW",
    "EXPO_PUBLIC_API_URL",
    "EXPO_PUBLIC_OAUTH_ISSUER",
    "EXPO_PUBLIC_OAUTH_CLIENT_ID",
  ] as const;
  const saved = Object.fromEntries(keys.map((key) => [key, process.env[key]]));
  try {
    process.env.EXPO_PUBLIC_HOSTED_PREVIEW = "false";
    process.env.EXPO_PUBLIC_API_URL =
      "https://abc123.execute-api.us-east-2.amazonaws.com/api";
    process.env.EXPO_PUBLIC_OAUTH_ISSUER =
      "https://cognito-idp.us-east-2.amazonaws.com/us-east-2_pool";
    process.env.EXPO_PUBLIC_OAUTH_CLIENT_ID = "actual-public-client";
    process.env.APP_ENV = process.env.EXPO_PUBLIC_APP_ENV = "qa";
    delete process.env.EXPO_PUBLIC_SERVERLESS;
    assert.equal(configure({ config: {} } as any).extra!.serverless, false);
    process.env.EXPO_PUBLIC_SERVERLESS = "true";
    assert.equal(configure({ config: {} } as any).extra!.serverless, true);
    process.env.APP_ENV = process.env.EXPO_PUBLIC_APP_ENV = "prod";
    assert.equal(configure({ config: {} } as any).extra!.serverless, true);
    for (const environment of ["local", "test"]) {
      process.env.APP_ENV = process.env.EXPO_PUBLIC_APP_ENV = environment;
      assert.throws(
        () => configure({ config: {} } as any),
        /require APP_ENV=qa or prod/,
      );
    }
    process.env.APP_ENV = process.env.EXPO_PUBLIC_APP_ENV = "qa";
    process.env.EXPO_PUBLIC_SERVERLESS = "yes";
    assert.throws(
      () => configure({ config: {} } as any),
      /must be true or false/,
    );
  } finally {
    for (const key of keys) {
      if (saved[key] === undefined) delete process.env[key];
      else process.env[key] = saved[key];
    }
  }
});
