#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PORT="${AGENT_BROWSER_CDP_PORT:-9222}"
BROWSER_BIN="${AGENT_BROWSER_CHROME:-}"
USER_DATA_DIR=""
PROFILE_DIRECTORY=""
START_URL="about:blank"

app_bundle_from_binary() {
  local binary_path="$1"
  case "$binary_path" in
    *.app/Contents/MacOS/*)
      printf '%s\n' "${binary_path%%/Contents/MacOS/*}"
      return 0
      ;;
    *)
      return 1
      ;;
  esac
}

detect_browser() {
  local candidates=(
    "$BROWSER_BIN"
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

while [[ $# -gt 0 ]]; do
  case "$1" in
    --port)
      PORT="$2"
      shift 2
      ;;
    --browser)
      BROWSER_BIN="$2"
      shift 2
      ;;
    --user-data-dir)
      USER_DATA_DIR="$2"
      shift 2
      ;;
    --profile-directory)
      PROFILE_DIRECTORY="$2"
      shift 2
      ;;
    --url)
      START_URL="$2"
      shift 2
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 1
      ;;
  esac
done

if ! browser_path="$(detect_browser)"; then
  echo "No Chrome or Chromium binary found." >&2
  exit 1
fi

if [[ -z "$USER_DATA_DIR" ]]; then
  USER_DATA_DIR="$ROOT_DIR/.tmp/chrome-cdp-profile"
  mkdir -p "$USER_DATA_DIR"
  echo "Using isolated profile: $USER_DATA_DIR"
else
  echo "Using explicit user data dir: $USER_DATA_DIR"
  echo "If you want real login state, fully quit Chrome before using this profile."
fi

cmd=(
  "--remote-debugging-port=$PORT"
  "--no-first-run"
  "--no-default-browser-check"
  "--user-data-dir=$USER_DATA_DIR"
)

if [[ -n "$PROFILE_DIRECTORY" ]]; then
  cmd+=("--profile-directory=$PROFILE_DIRECTORY")
fi

cmd+=("$START_URL")

if [[ "$(uname -s)" == "Darwin" ]] && app_bundle="$(app_bundle_from_binary "$browser_path")"; then
  /usr/bin/open -na "$app_bundle" --args "${cmd[@]}" >/dev/null 2>&1 &
else
  "$browser_path" "${cmd[@]}" >/dev/null 2>&1 &
fi

echo "Started Chrome CDP instance."
echo "Browser: $browser_path"
echo "Port: $PORT"
echo "URL: $START_URL"
