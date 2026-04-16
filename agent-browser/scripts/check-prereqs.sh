#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WRAPPER="$ROOT_DIR/scripts/cdpctl.sh"
HOST="${AGENT_BROWSER_CDP_HOST:-127.0.0.1}"
PORT="${AGENT_BROWSER_CDP_PORT:-9222}"

detect_browser() {
  local candidates=(
    "${AGENT_BROWSER_CHROME:-}"
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    "$HOME/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    "/Applications/Chromium.app/Contents/MacOS/Chromium"
    "$HOME/Applications/Chromium.app/Contents/MacOS/Chromium"
    "$(command -v google-chrome 2>/dev/null || true)"
    "$(command -v chromium 2>/dev/null || true)"
    "$(command -v chromium-browser 2>/dev/null || true)"
    "$(command -v chrome 2>/dev/null || true)"
  )
  local candidate
  for candidate in "${candidates[@]}"; do
    if [[ -n "$candidate" && -x "$candidate" ]]; then
      echo "$candidate"
      return 0
    fi
  done
  return 1
}

echo "Workspace: $ROOT_DIR"
echo "CDP endpoint: http://$HOST:$PORT"

if ! command -v python3 >/dev/null 2>&1; then
  echo "Missing python3." >&2
  exit 1
fi

if browser_path="$(detect_browser)"; then
  echo "Browser: $browser_path"
else
  echo "No Chrome or Chromium binary found." >&2
  exit 1
fi

if [[ ! -x "$WRAPPER" ]]; then
  echo "Wrapper is missing or not executable: $WRAPPER" >&2
  exit 1
fi

if ! command -v curl >/dev/null 2>&1; then
  echo "Missing curl." >&2
  exit 1
fi

if ! version_json="$(curl -fsS "http://$HOST:$PORT/json/version" 2>/dev/null)"; then
  echo "CDP endpoint is not reachable." >&2
  echo "Start Chrome with ./scripts/launch-chrome-cdp.sh and retry." >&2
  exit 1
fi

echo "Endpoint metadata: $version_json"
echo "agent-browser preflight OK"
