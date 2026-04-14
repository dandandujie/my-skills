# CDP Bridge Patterns

## Table of Contents
- [Batch Commands](#batch-commands)
- [File Upload](#file-upload)
- [Autofill & Login](#autofill--login)
- [Cross-Origin Iframe](#cross-origin-iframe)
- [CDP Click Lifecycle](#cdp-click-lifecycle)
- [CDP Text Input](#cdp-text-input)
- [Shadow DOM Traversal](#shadow-dom-traversal)
- [Screenshots & Canvas](#screenshots--canvas)
- [PDF Download](#pdf-download)
- [Google Image Search](#google-image-search)
- [Extension Management](#extension-management)
- [Coordinate Correction](#coordinate-correction)

---

## Batch Commands

Single request, multiple commands. CDP commands share one debugger session (lazy attach, auto-detach).

```json
{"cmd": "batch", "tabId": N, "commands": [
  {"cmd": "cookies"},
  {"cmd": "tabs"},
  {"cmd": "cdp", "method": "DOM.getDocument", "params": {"depth": 1}},
  {"cmd": "cdp", "method": "DOM.querySelector", "params": {"nodeId": "$2.root.nodeId", "selector": "h1"}}
]}
```

**Cross-reference syntax**: `"$N.path.to.field"` — N is 0-indexed command result.

Rules:
- Sub-commands inherit outer tabId (cookies command auto-resolves current page URL)
- If command N fails, `$N+1.xxx` refs silently become undefined — always check `results[i].ok`
- Keep nodeId source consistent within one chain: don't mix querySelector path with performSearch path
- CDP default tab = sender.tab.id (current injected page); cross-tab needs explicit tabId or batch-internal tabs query first

## File Upload

JS cannot fill `<input type=file>` (security). Use CDP batch:

```json
{"cmd": "batch", "tabId": N, "commands": [
  {"cmd": "cdp", "method": "DOM.getDocument", "params": {"depth": 1}},
  {"cmd": "cdp", "method": "DOM.querySelector", "params": {"nodeId": "$0.root.nodeId", "selector": "input[type=file]"}},
  {"cmd": "cdp", "method": "DOM.setFileInputFiles", "params": {"nodeId": "$1.nodeId", "files": ["/absolute/path/to/file"]}}
]}
```

Tips:
- **depth:1** on getDocument is sufficient for querySelector
- Check `input.accept` attribute before upload; multiple inputs — distinguish by accept or parent container semantics
- After upload, frontend framework may not detect change — dispatch `input`+`change` events via JS:
  ```js
  el.dispatchEvent(new Event('input', {bubbles: true}));
  el.dispatchEvent(new Event('change', {bubbles: true}));
  ```
- Wait for element: prefer `DOM.performSearch('input[type=file]')` for lightweight polling
- Transient inputs: minimize discover-to-setFileInputFiles time window; prefer same-batch completion; fallback to DOM event listener; monkey-patch as last resort
- Fallback: ljqCtrl physical click to open file dialog

## Autofill & Login

Detection: `web_scan` shows input with `data-autofilled="true"`, value shows protected placeholder (Chrome protects real values until user interaction).

**Prerequisite**: Must `Page.bringToFront` to switch tab to foreground — Chrome only releases autofill values in foreground tab.

One-shot release + login:
```json
{"cmd": "batch", "tabId": N, "commands": [
  {"cmd": "cdp", "method": "Page.bringToFront"},
  {"cmd": "cdp", "method": "Input.dispatchMouseEvent", "params": {
    "type": "mousePressed", "x": 100, "y": 200, "button": "left", "clickCount": 1
  }}
]}
```
Then wait 500ms, dispatch `input`+`change` events on fields, and click login button.

Key: `mousePressed` alone (no Released needed) releases ALL autofill fields on the page.

## Cross-Origin Iframe

`Target.getTargets`/`Target.attachToTarget` returns "Not allowed" under chrome.debugger.

**Verified approach**:
1. `Page.getFrameTree` — find iframe's frameId by URL match in `childFrames`
2. `Page.createIsolatedWorld({frameId})` — get executionContextId
3. `Runtime.evaluate({expression, contextId})` — execute JS inside iframe

Batch chain:
```json
{"cmd": "batch", "tabId": N, "commands": [
  {"cmd": "cdp", "method": "Page.getFrameTree"},
  {"cmd": "cdp", "method": "Page.createIsolatedWorld", "params": {"frameId": "FRAME_ID_FROM_STEP_0"}},
  {"cmd": "cdp", "method": "Runtime.evaluate", "params": {
    "expression": "document.title",
    "contextId": "$1.executionContextId",
    "returnByValue": true
  }}
]}
```

Note: `$0.frameTree.childFrames` — iterate to find URL-matching frame. postMessage relay only works if content script is already injected in iframe (third-party payment iframes typically lack injection).

## CDP Click Lifecycle

Full click requires **three-event sequence** with 50-100ms gaps:
1. `Input.dispatchMouseEvent` type: `mouseMoved` (x, y)
2. `Input.dispatchMouseEvent` type: `mousePressed` (x, y, button: "left", clickCount: 1)
3. `Input.dispatchMouseEvent` type: `mouseReleased` (x, y, button: "left", clickCount: 1)

Skipping `mouseMoved` breaks hover-dependent components (MUI Tooltip, Ant Design Dropdown).

Exception: autofill release only needs `mousePressed`.

JS click opens new tab but blocked? Likely browser popup blocker — switch to CDP click.

## CDP Text Input

- `Input.insertText` — fast but generates no key events; React/Vue controlled components need manual `input` event dispatch
- Full keyboard simulation: `Input.dispatchKeyEvent` per key (`keyDown` -> `keyUp`)
- For controlled components after insertText:
  ```js
  el.dispatchEvent(new Event('input', {bubbles: true}));
  ```

## Shadow DOM Traversal

Penetrate closed Shadow DOM:
```json
{"cmd": "cdp", "method": "DOM.getDocument", "params": {"depth": -1, "pierce": true}}
```
Then `DOM.querySelector({nodeId, selector})` -> `DOM.getBoxModel({nodeId})` for coordinates.

getBoxModel returns content quad: `[x1,y1,x2,y2,x3,y3,x4,y4]`. Center = **four-point average**:
```
centerX = (x1+x2+x3+x4)/4
centerY = (y1+y2+y3+y4)/4
```
Do NOT simplify to diagonal average — element may have transform:rotate/skew making quad non-rectangular.

querySelector **cannot cross Shadow boundary in a single combined selector** — find host first, then querySelector within its shadow subtree.

## Screenshots & Canvas

**Page screenshot** (works on background tabs too):
```json
{"cmd": "cdp", "method": "Page.captureScreenshot", "params": {"format": "png"}}
```
Returns base64-encoded image.

**Canvas/captcha**: JS `canvas.toDataURL()` is cleanest for extracting canvas content as base64.

## PDF Download

For PDF links that open in browser preview instead of downloading:
```js
fetch('PDF_URL').then(r=>r.blob()).then(b=>{
  const a=document.createElement('a');
  a.href=URL.createObjectURL(b);
  a.download='filename.pdf';
  a.click();
});
```
Requires same-origin or CORS. Cross-origin: navigate to target domain first, then execute.

## Google Image Search

- Class names are obfuscated — never hardcode. Click results via `[role=button]` divs.
- After popup: text via `document.body.innerText`, large image via iterating `img` by max `naturalWidth`
- "Visit" link: find `a` where `textContent.includes('访问')` and take href
- Thumbnails: `img[src^="data:image"]` for extraction; large image src may be truncated — use `return img.src`

## Extension Management

```json
{"cmd": "management", "method": "list"}       // list all extensions
{"cmd": "management", "method": "reload"}      // reload CDP bridge extension itself
{"cmd": "management", "method": "disable", "extId": "xxx"}
{"cmd": "management", "method": "enable", "extId": "xxx"}
```

## Coordinate Correction

When page has `transform:scale` or `zoom`:
```js
var scale = window.visualViewport ? window.visualViewport.scale : 1;
var zoom = parseFloat(getComputedStyle(document.documentElement).zoom) || 1;
var realX = x * zoom;
var realY = y * zoom;
```

Iframe element CDP click — composite coordinates:
```
finalX = iframeRect.x + elementRect.x
finalY = iframeRect.y + elementRect.y
```
