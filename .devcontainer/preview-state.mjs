import { createHash } from "node:crypto";
import { execFileSync } from "node:child_process";
import { mkdirSync, readFileSync, readdirSync, writeFileSync } from "node:fs";
import { dirname, relative, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const dist = resolve(root, "apps/mobile/dist-preview");
const receipt = resolve(root, ".local/codespaces-preview/prepared.json");
const hash = (value) => createHash("sha256").update(value).digest("hex");
const git = (...args) =>
  execFileSync("git", args, { cwd: root, encoding: "utf8" }).trim();

function sourceState() {
  const paths = new Set(
    git(
      "ls-files",
      "--cached",
      "--others",
      "--exclude-standard",
      "--",
      "apps/mobile",
      ".devcontainer",
    )
      .split("\n")
      .filter(Boolean),
  );
  // Include these scripts before their first commit as well.
  for (const name of [
    "prepare-preview.sh",
    "start-preview.sh",
    "preview-state.mjs",
  ])
    paths.add(`.devcontainer/${name}`);
  return {
    source_revision: git("rev-parse", "HEAD"),
    source_dirty: Boolean(
      git("status", "--porcelain", "--", "apps/mobile", ".devcontainer"),
    ),
    source_fingerprint: hash(
      JSON.stringify(
        [...paths]
          .sort()
          .map((path) => [path, hash(readFileSync(resolve(root, path)))]),
      ),
    ),
  };
}

function exportFingerprint(directory = dist) {
  const entries = [];
  for (const entry of readdirSync(directory, { withFileTypes: true })) {
    const path = resolve(directory, entry.name);
    if (entry.isSymbolicLink())
      throw Error("Preview export must not contain symlinks");
    if (entry.isDirectory()) entries.push(...exportFingerprint(path));
    else if (entry.isFile())
      entries.push([relative(dist, path), hash(readFileSync(path))]);
    else throw Error("Unexpected preview export entry");
  }
  return entries.sort(([a], [b]) => a.localeCompare(b));
}

function expected() {
  const manifestBytes = readFileSync(resolve(dist, "preview-manifest.json"));
  const manifest = JSON.parse(manifestBytes);
  const build = manifest.build_environment;
  if (
    manifest.schema_version !== "1.0.0" ||
    manifest.environment !== "local" ||
    manifest.fictional_guest_only !== true ||
    manifest.account_services !== false ||
    manifest.sensor_permissions !== false ||
    manifest.raw_recording !== false ||
    manifest.uploads !== false ||
    manifest.inference_available !== false ||
    manifest.persistence !== "browser_memory_only" ||
    build?.APP_ENV !== "local" ||
    build.EXPO_PUBLIC_APP_ENV !== "local" ||
    build.EXPO_PUBLIC_HOSTED_PREVIEW !== "true" ||
    build.EXPO_PUBLIC_SERVERLESS !== "false" ||
    build.EXPO_NO_DOTENV !== "1" ||
    build.EXPO_PUBLIC_API_URL !== "https://unavailable.invalid" ||
    build.EXPO_PUBLIC_OAUTH_ISSUER !== "https://unavailable.invalid" ||
    build.EXPO_PUBLIC_OAUTH_CLIENT_ID !== "otgd-hosted-fictional"
  )
    throw Error("Rebuild the isolated fictional guest export");
  const indexBytes = readFileSync(resolve(dist, "index.html"));
  if (!indexBytes.length) throw Error("Missing preview index");
  return {
    mode: "fictional_guest",
    ...sourceState(),
    export_sha256: hash(JSON.stringify(exportFingerprint())),
    manifest_sha256: hash(manifestBytes),
    index_sha256: hash(indexBytes),
  };
}

function checked() {
  const actual = JSON.parse(readFileSync(receipt));
  const current = expected();
  if (Object.entries(current).some(([key, value]) => actual[key] !== value))
    throw Error(
      "Guest source or export changed; rebuild the Codespace before starting it",
    );
  return current;
}

async function boundedBody(response) {
  if (!response.ok || !response.body)
    throw Error("Unexpected preview response");
  const parts = [];
  let size = 0;
  for await (const part of response.body) {
    size += part.length;
    if (size > 16384) throw Error("Unexpected oversized preview response");
    parts.push(Buffer.from(part));
  }
  return Buffer.concat(parts);
}

try {
  const command = process.argv[2];
  if (command === "prepare") {
    const value = expected();
    mkdirSync(dirname(receipt), { recursive: true });
    writeFileSync(
      receipt,
      JSON.stringify(
        {
          ...value,
          node: process.version,
          prepared_at: new Date().toISOString(),
        },
        null,
        2,
      ) + "\n",
    );
  } else if (command === "check") {
    checked();
  } else if (command === "ready") {
    const current = checked();
    const port = Number(process.argv[3]);
    if (!Number.isInteger(port) || port < 1024 || port > 65535)
      throw Error("Invalid preview port");
    for (const [path, digest] of [
      ["preview-manifest.json", current.manifest_sha256],
      ["", current.index_sha256],
    ]) {
      let response;
      try {
        response = await fetch(`http://127.0.0.1:${port}/${path}`, {
          signal: AbortSignal.timeout(1500),
          redirect: "error",
        });
      } catch (error) {
        if (error.cause?.code === "ECONNREFUSED") process.exit(1);
        throw error;
      }
      if (hash(await boundedBody(response)) !== digest)
        throw Error("The port does not serve the prepared guest export");
    }
  } else {
    throw Error("Use prepare, check, or ready");
  }
} catch (error) {
  console.error(error.message);
  process.exit(2);
}
