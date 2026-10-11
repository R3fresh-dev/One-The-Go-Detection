import { spawnSync } from "node:child_process";
import { readdirSync, readFileSync, rmSync, mkdirSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { resolve, dirname } from "node:path";
const root = resolve(dirname(fileURLToPath(import.meta.url)), ".."),
  report = resolve(root, "reports/mobile-unit-coverage.json");
mkdirSync(resolve(root, "reports"), { recursive: true });
rmSync(report, { force: true });
const tests = ["tests", "src/device/tests"].flatMap((directory) =>
  readdirSync(resolve(root, directory))
    .filter((name) => name.endsWith(".test.ts"))
    .map((name) => directory + "/" + name),
);
if (!tests.length) throw Error("No mobile unit tests discovered");
const outcome = spawnSync(
  process.execPath,
  [
    "--import",
    "tsx",
    "--test",
    "--experimental-test-coverage",
    "--test-coverage-include=src/**/*.ts",
    "--test-coverage-exclude=src/device/tests/**",
    "--test-reporter=spec",
    "--test-reporter-destination=stdout",
    "--test-reporter=./scripts/coverage-reporter.mjs",
    "--test-reporter-destination=reports/mobile-unit-events.log",
    ...tests,
  ],
  { cwd: root, stdio: "inherit" },
);
if (outcome.error) throw outcome.error;
let result;
try {
  result = JSON.parse(readFileSync(report, "utf8"));
} catch {
  throw Error("Fresh executable coverage report was not produced");
}
console.log(
  `Mobile executable TypeScript unit coverage: ${result.totals.percent_covered.toFixed(2)}% (required >80%); unloaded: ${result.unloaded_source_files.join(", ") || "none"}.`,
);
if (
  outcome.status !== 0 ||
  !result.passed ||
  result.totals.percent_covered <= 80
)
  process.exit(1);
