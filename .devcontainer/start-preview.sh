#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
test -f .local/codespaces-preview/prepared.json
test -f apps/mobile/dist/index.html
# Codespaces may invoke postStart again. Leave the existing preview server alone.
if node -e 'fetch("http://127.0.0.1:8082/").then(r=>process.exit(r.ok?0:1)).catch(()=>process.exit(1))'; then
  exit 0
fi
cd apps/mobile
nohup node scripts/serve-web.mjs > ../../.local/codespaces-preview/server.log 2>&1 < /dev/null &
otgd_preview_pid=$!
printf '%s\n' "$otgd_preview_pid" > ../../.local/codespaces-preview/server.pid
for otgd_preview_attempt in {1..30}; do
  if node -e 'fetch("http://127.0.0.1:8082/").then(r=>process.exit(r.ok?0:1)).catch(()=>process.exit(1))'; then
    exit 0
  fi
  kill -0 "$otgd_preview_pid"
  sleep 1
done
printf '%s\n' 'Preview server did not become ready; inspect .local/codespaces-preview/server.log.' >&2
exit 1
