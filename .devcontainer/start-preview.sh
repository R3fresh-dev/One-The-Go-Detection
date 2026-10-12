#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
node .devcontainer/preview-state.mjs check
otgd_preview_port="${OTGD_PREVIEW_PORT:-8082}"
# Repeated lifecycle hooks may reuse only this exact prepared guest export.
if node .devcontainer/preview-state.mjs ready "$otgd_preview_port"; then
  exit 0
else
  otgd_preview_status=$?
  if [ "$otgd_preview_status" -ne 1 ]; then
    printf '%s\n' 'The preview port serves unexpected content; stop that process or rebuild the Codespace.' >&2
    exit 1
  fi
fi
cd apps/mobile
OTGD_WEB_DIST=dist-preview OTGD_WEB_PORT="$otgd_preview_port" nohup node scripts/serve-web.mjs > ../../.local/codespaces-preview/server.log 2>&1 < /dev/null &
otgd_preview_pid=$!
printf '%s\n' "$otgd_preview_pid" > ../../.local/codespaces-preview/server.pid
for otgd_preview_attempt in {1..30}; do
  if node ../../.devcontainer/preview-state.mjs ready "$otgd_preview_port"; then
    exit 0
  fi
  kill -0 "$otgd_preview_pid"
  sleep 1
done
printf '%s\n' 'Preview server did not become ready; inspect .local/codespaces-preview/server.log.' >&2
exit 1
