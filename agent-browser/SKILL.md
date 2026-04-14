---
name: agent-browser
description: >
  Browser automation via TMWebDriver (Chrome extension CDP bridge) and ljqCtrl (physical input).
  Use when: controlling a real browser (not Selenium/Playwright), executing JS on pages, reading page
  content, CDP operations (cookies/tabs/file upload/screenshots/autofill), clicking elements that
  require isTrusted events, physical mouse/keyboard simulation, cross-origin iframe interaction,
  or any task involving web_scan, web_execute_js, TMWebDriver, CDP bridge, ljqCtrl, or browser tab
  management. Preserves user login state and cookies — operates on the user's live browser session.
---

# Agent Browser

Three-layer browser automation stack operating on the user's real Chrome browser (preserves login/cookies):

| Layer | Tool | When |
|-------|------|------|
| Read | `web_scan` | Read page content (auto-traverses same-origin iframes) |
| JS/CDP | `web_execute_js` | Execute JS or send CDP commands via JSON |
| Physical | `ljqCtrl` | Physical mouse/keyboard when JS/CDP can't (isTrusted) |

## Core Tools

### web_scan — Read Page

Read-only snapshot of current page. Does NOT navigate. Cross-origin iframes need CDP (see references).

### web_execute_js — Execute JS

```
web_execute_js script='document.title'
web_execute_js script='location.href="https://example.com"'  // navigate
```

**Critical**: with `await`, must use explicit `return` — the code is wrapped in async, omitting return yields null:
```js
// WRONG: returns null
await fetch('/api').then(r => r.json())
// RIGHT:
return await fetch('/api').then(r => r.json())
```

### CDP Bridge — via JSON to web_execute_js

Pass JSON string as script; the tool layer routes it through WebSocket to the Chrome extension's background.js:

```
web_execute_js script='{"cmd": "tabs"}'
web_execute_js script='{"cmd": "cookies"}'
web_execute_js script='{"cmd": "cdp", "tabId": N, "method": "Page.captureScreenshot", "params": {"format": "png"}}'
web_execute_js script='{"cmd": "management", "method": "list"}'
```

**Batch** (single request, multiple commands, CDP session reuse):
```
web_execute_js script='{"cmd": "batch", "commands": [
  {"cmd": "cdp", "method": "DOM.getDocument", "params": {"depth": 1}},
  {"cmd": "cdp", "method": "DOM.querySelector", "params": {"nodeId": "$0.root.nodeId", "selector": "input[type=file]"}},
  {"cmd": "cdp", "method": "DOM.setFileInputFiles", "params": {"nodeId": "$1.nodeId", "files": ["/path/to/file"]}}
]}'
```
- `$N.path` references the Nth result (0-indexed): `"$0.root.nodeId"` = result[0].root.nodeId
- Sub-commands inherit outer batch's tabId
- If command N fails, `$N+1` refs silently become undefined — check each result's ok status

## Essential Rules

1. **JS events are isTrusted=false** — sensitive ops (file upload, some buttons) may be blocked. Use CDP or ljqCtrl.
2. **Navigation**: `web_scan` never navigates. Use `web_execute_js` + `location.href='url'`.
3. **Extension reload**: After extension update, old tabs' content scripts don't reload — must refresh pages.
4. **Background tab throttling**: Chrome throttles `setTimeout` to >= 1min in background tabs. Don't rely on setTimeout polling in extension scripts.
5. **Cross-tab CDP**: Specify `tabId` to operate on any tab (including background) — no need to bring to front (except autofill).
6. **nodeId instability**: nodeId invalidates after DOM mutation. Use `backendNodeId` for stability, or re-call `getDocument`.

## Key Scenarios Quick Ref

| Scenario | Approach | Reference |
|----------|----------|----------|
| File upload | CDP batch: getDocument(depth:1) -> querySelector -> setFileInputFiles | [cdp-bridge.md](references/cdp-bridge.md) |
| Autofill login | bringToFront -> mousePressed -> wait 500ms -> submit | [cdp-bridge.md](references/cdp-bridge.md) |
| Cross-origin iframe | getFrameTree -> createIsolatedWorld -> Runtime.evaluate | [cdp-bridge.md](references/cdp-bridge.md) |
| Screenshot | `Page.captureScreenshot` (works on background tabs) | [cdp-bridge.md](references/cdp-bridge.md) |
| CDP click | mouseMoved -> mousePressed -> mouseReleased (50-100ms gaps) | [cdp-bridge.md](references/cdp-bridge.md) |
| Shadow DOM | getDocument({depth:-1, pierce:true}) | [cdp-bridge.md](references/cdp-bridge.md) |
| Physical click/type | ljqCtrl with DPI coordinate conversion | [physical-input.md](references/physical-input.md) |
| Google image search | Use `[role=button]` not class names (obfuscated) | [cdp-bridge.md](references/cdp-bridge.md) |
| PDF download | fetch -> blob -> createObjectURL -> a.click() (same-origin) | [cdp-bridge.md](references/cdp-bridge.md) |

## Troubleshooting

web_scan/web_execute_js fails — check in order:
1. Extension installed? Check chrome://extensions for TMWD CDP Bridge
2. Browser running? Verify process is alive; `about:blank` won't load extensions — open a real URL
3. WebSocket server dead? `socket.connect_ex(('127.0.0.1', 18766))` != 0 means dead -> start `TMWebDriver()`
