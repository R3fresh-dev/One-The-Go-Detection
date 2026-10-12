#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../apps/mobile"
test "$(node --version)" = "v24.19.0"
npm ci
npm run typecheck
npm run export:preview
node ../../.devcontainer/preview-state.mjs prepare
