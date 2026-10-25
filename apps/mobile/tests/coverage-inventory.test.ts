import test from "node:test";
import assert from "node:assert/strict";
import { resolve } from "node:path";
const { productionUnitSources } =
  require("../scripts/coverage-reporter.mjs") as {
    productionUnitSources(directory?: string): string[];
  };

test("the shared JavaScript OAuth validator remains in the independent executable unit coverage inventory", () => {
  const files = productionUnitSources();
  const policy = resolve("oauth-build-policy.js");
  assert.equal(files.filter((file) => file === policy).length, 1);
  assert.ok(files.includes(resolve("src/core/oauthPolicy.ts")));
  assert.ok(files.includes(resolve("src/services/auth.ts")));
  assert.ok(
    !files.some((file) => file.endsWith(".d.ts") || file.includes("/tests/")),
  );
});
