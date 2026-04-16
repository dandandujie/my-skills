# GenericAgent Zero-Plugin Setup

This setup replaces the old Chrome extension bridge with Chrome remote debugging.

## 1. Choose The Browser Profile Mode

There are two valid startup modes:

1. Safer default: use the local temporary profile created by `./scripts/launch-chrome-cdp.sh`.
2. Real login state: relaunch Chrome with your real `--user-data-dir` and `--profile-directory`.

If you want the real logged-in profile, fully quit Chrome first. A Chrome process that was already running without `--remote-debugging-port` will usually ignore a later launch attempt that adds it.

## 2. Start Chrome With Remote Debugging

Run the preflight:

```bash
./scripts/check-prereqs.sh
```

If the CDP endpoint is not available yet, start Chrome:

```bash
./scripts/launch-chrome-cdp.sh
```

If you need a real Chrome profile instead of the temporary one, pass the profile explicitly. Example on macOS:

```bash
./scripts/launch-chrome-cdp.sh \
  --user-data-dir "$HOME/Library/Application Support/Google/Chrome" \
  --profile-directory Default
```

## 3. First Verification

Verify that the endpoint is live:

```bash
./scripts/cdpctl.sh version
./scripts/cdpctl.sh tabs
```

Then open a page if needed:

```bash
./scripts/cdpctl.sh open https://example.com
./scripts/cdpctl.sh tabs
```

If `version` or `tabs` fails, do not continue with browser automation commands.

## 4. Troubleshooting Order

When browser commands fail, check in this order:

1. Chrome was started with `--remote-debugging-port`.
2. The endpoint at `http://127.0.0.1:9222/json/version` is reachable.
3. The target is a normal web page, not a `chrome://...` page.
4. If you intended to reuse the real browser profile, Chrome was fully closed before relaunch.

## 5. Scope Boundary

- This repository no longer depends on `tmwd_cdp_bridge`.
- The zero-plugin path still supports raw CDP methods, cookies, screenshots, tabs, clicks, typing, and file uploads.
- `ljqCtrl` remains a separate physical-input layer and is not bundled here.
