import { readFileSync, readdirSync, mkdirSync, writeFileSync } from "node:fs";
import { resolve, relative, join } from "node:path";
import { createHash } from "node:crypto";
import ts from "typescript";
const root = process.cwd(),
  reports = resolve(root, "reports");
function files(directory) {
  return readdirSync(directory, { withFileTypes: true }).flatMap((entry) =>
    entry.isDirectory()
      ? files(join(directory, entry.name))
      : [join(directory, entry.name)],
  );
}
function runtimeSource(path) {
  const tree = ts.createSourceFile(
    path,
    readFileSync(path, "utf8"),
    ts.ScriptTarget.Latest,
    true,
  );
  return tree.statements.some((statement) => {
    if (
      ts.isInterfaceDeclaration(statement) ||
      ts.isTypeAliasDeclaration(statement)
    )
      return false;
    if (ts.isImportDeclaration(statement)) return !statement.importClause; // Side-effect imports execute; typed dependency declarations do not create behavior.
    if (ts.isExportDeclaration(statement))
      return !statement.isTypeOnly && !!statement.moduleSpecifier;
    if (
      statement.modifiers?.some(
        (modifier) => modifier.kind === ts.SyntaxKind.DeclareKeyword,
      )
    )
      return false;
    return true;
  });
}
export default async function* coverageReporter(source) {
  let coverage, summary;
  for await (const event of source) {
    if (event.type === "test:coverage") coverage = event.data.summary;
    if (event.type === "test:summary") summary = event.data;
  }
  const inventory = files(resolve(root, "src")).filter(
    (path) =>
      path.endsWith(".ts") &&
      !path.endsWith(".d.ts") &&
      !path.includes("/tests/"),
  );
  const executable = inventory.filter(runtimeSource),
    types = inventory.filter((path) => !runtimeSource(path));
  const observed = new Map(
    (coverage?.files ?? []).map((file) => [resolve(file.path), file]),
  );
  const hash = createHash("sha256");
  const results = executable.map((path) => {
    const bytes = readFileSync(path);
    hash.update(relative(root, path) + "\0");
    hash.update(bytes);
    const entry = observed.get(path);
    return {
      path: relative(root, path),
      loaded: !!entry,
      total_lines: entry?.totalLineCount ?? bytes.toString().split("\n").length,
      covered_lines: entry?.coveredLineCount ?? 0,
      line_percent: entry?.coveredLinePercent ?? 0,
    };
  });
  const total = results.reduce((n, file) => n + file.total_lines, 0),
    covered = results.reduce((n, file) => n + file.covered_lines, 0),
    percent = total ? (100 * covered) / total : 0;
  const counts = summary?.counts ?? {
    tests: 0,
    failed: 0,
    cancelled: 0,
    skipped: 0,
    todo: 0,
  };
  const passed =
    !!coverage &&
    !!summary &&
    counts.tests > 0 &&
    counts.failed === 0 &&
    counts.cancelled === 0 &&
    counts.skipped === 0 &&
    counts.todo === 0 &&
    percent > 80;
  const report = {
    schema_version: "1.0.0",
    created_at: new Date().toISOString(),
    scope:
      "Every executable src/**/*.ts business module, including unloaded modules counted as zero. TSX views use the separate browser component/ATDD gate; native OS adapters remain in this inventory. Native boundary mocks do not establish physical qualification.",
    source_sha256: hash.digest("hex"),
    required_percent_strictly_greater_than: 80,
    passed,
    counts,
    totals: {
      total_lines: total,
      covered_lines: covered,
      percent_covered: percent,
    },
    files: results,
    unloaded_source_files: results
      .filter((file) => !file.loaded)
      .map((file) => file.path),
    type_only_sources: types.map((path) => relative(root, path)),
    browser_component_sources: files(resolve(root, "src"))
      .filter((path) => path.endsWith(".tsx"))
      .map((path) => relative(root, path)),
  };
  mkdirSync(reports, { recursive: true });
  writeFileSync(
    join(reports, "mobile-unit-coverage.json"),
    JSON.stringify(report, null, 2) + "\n",
  );
  yield `Executable TypeScript unit coverage: ${percent.toFixed(2)}% (required >80%); ${counts.tests} tests, ${counts.failed} failed, ${counts.skipped} skipped.\n`;
  if (!passed) {
    process.exitCode = 1;
    yield "FAILED: missing coverage, zero tests, failed/canceled/skipped/TODO tests, or coverage at/below 80%.\n";
  }
}
