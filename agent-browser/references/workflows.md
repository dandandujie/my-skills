# Zero-Plugin Browser Workflows

## 1. Preflight

Start with:

```bash
./scripts/check-prereqs.sh
```

If Chrome is not already exposing a CDP endpoint, launch it:

```bash
./scripts/launch-chrome-cdp.sh
```

Then verify:

```bash
./scripts/cdpctl.sh version
./scripts/cdpctl.sh tabs
```

## 2. Open A Page And Read It

```bash
./scripts/cdpctl.sh open https://example.com
./scripts/cdpctl.sh tabs
./scripts/cdpctl.sh eval example.com "document.title"
./scripts/cdpctl.sh eval example.com "document.body.innerText.slice(0, 1000)"
```

`<target>` can be a target id, a URL substring, or a title substring.

## 3. Navigate

```bash
./scripts/cdpctl.sh navigate example.com https://example.com/login
./scripts/cdpctl.sh eval example.com "location.href"
```

## 4. Click And Type

```bash
./scripts/cdpctl.sh click example.com 'button[type=submit]'
./scripts/cdpctl.sh type example.com 'input[name=email]' 'user@example.com' --clear
./scripts/cdpctl.sh type example.com 'input[name=password]' 'correct horse battery staple' --clear
```

If the site is unusually sensitive, fall through to `raw` and use lower-level CDP input methods directly.

## 5. File Upload

For a straightforward file input:

```bash
./scripts/cdpctl.sh upload example.com 'input[type=file]' /absolute/path/to/file.pdf
```

For a chained CDP workflow:

```bash
./scripts/cdpctl.sh batch example.com --json '[
  {"method":"DOM.getDocument","params":{"depth":1}},
  {"method":"DOM.querySelector","params":{"nodeId":"$0.root.nodeId","selector":"input[type=file]"}},
  {"method":"DOM.setFileInputFiles","params":{"nodeId":"$1.nodeId","files":["/absolute/path/to/file.pdf"]}}
]'
```

## 6. Cookies, Tabs, And Screenshots

```bash
./scripts/cdpctl.sh cookies example.com
./scripts/cdpctl.sh tabs
./scripts/cdpctl.sh screenshot example.com --output /tmp/example.png
```

## 7. Raw CDP Commands

Use `raw` when there is no higher-level wrapper:

```bash
./scripts/cdpctl.sh raw example.com Page.captureScreenshot --params '{"format":"png"}'
./scripts/cdpctl.sh raw example.com Runtime.evaluate --params '{"expression":"document.readyState","returnByValue":true}'
```

## 8. Cross-Origin Iframe

Stay at raw CDP level:

1. `Page.getFrameTree`
2. `Page.createIsolatedWorld`
3. `Runtime.evaluate`

The zero-plugin path does not hide this complexity.

## 9. Boundary Cases

If the task still needs true OS-level mouse movement, clipboard paste into native dialogs, or other desktop-native control, stop and say the browser CDP path is insufficient.
