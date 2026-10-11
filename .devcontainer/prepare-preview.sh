#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../apps/mobile"
test "$(node --version)" = "v24.19.0"
npm ci
npm run typecheck
APP_ENV=local EXPO_PUBLIC_HOSTED_PREVIEW=true npm run export:web
mkdir -p ../../.local/codespaces-preview
node -e 'require("fs").writeFileSync("../../.local/codespaces-preview/prepared.json",JSON.stringify({mode:"fictional_guest",node:process.version,preparedAt:new Date().toISOString()}))'
