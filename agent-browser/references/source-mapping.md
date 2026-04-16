# GenericAgent To Zero-Plugin CDP Map

This skill keeps the GenericAgent operating style, but swaps the browser extension for local Chrome DevTools Protocol scripts.

| Original idea | Zero-plugin replacement | Notes |
|---|---|---|
| `web_scan` current-page reads | `./scripts/cdpctl.sh eval <target> "document.body.innerText"` | Use `eval` for page text, titles, selectors, and small reads. |
| `web_execute_js` | `./scripts/cdpctl.sh eval <target> "<js>"` | Use this for DOM reads, DOM writes, and navigation. |
| `tmwd_cdp_bridge` cookies | `./scripts/cdpctl.sh cookies <target>` | No extension required as long as Chrome was launched with remote debugging. |
| `tmwd_cdp_bridge` tabs | `./scripts/cdpctl.sh tabs`, `open`, `activate`, `close` | Use target id, title substring, or URL substring to select a page. |
| Direct CDP command | `./scripts/cdpctl.sh raw <target> <method> --params '<json>'` | Best for methods not covered by a higher-level command. |
| Bridge `batch` chains | `./scripts/cdpctl.sh batch <target> --json '<json>'` | Supports `$0.path` references into earlier results. |
| CDP screenshot | `./scripts/cdpctl.sh screenshot <target> --output file.png` | Uses `Page.captureScreenshot`. |
| CDP file upload | `./scripts/cdpctl.sh upload <target> '<selector>' /path/file` | Uses `DOM.setFileInputFiles`. |
| Sensitive click flow | `./scripts/cdpctl.sh click <target> '<selector>'` | Uses `Input.dispatchMouseEvent`. |
| Text entry | `./scripts/cdpctl.sh type <target> '<selector>' 'text'` | Uses CDP focus plus `Input.insertText`. |
| Cross-origin iframe work | `raw` or `batch` with frame methods | Keep it at raw CDP level. |
| `ljqCtrl` fallback | No built-in replacement | Say so plainly if the task truly needs OS-level physical input. |

## Decision Order

1. Use `eval` if the task is normal page reading or DOM work.
2. Use `click`, `type`, `upload`, `cookies`, `screenshot`, or `navigate` if a high-level command already exists.
3. Use `raw` or `batch` for frame work, trusted flows, or other lower-level CDP commands.
4. Stop and state the boundary if the task actually needs desktop-native physical input.

## Non-Negotiable Constraints

- Chrome must be running with `--remote-debugging-port`.
- If you need the real logged-in profile, Chrome must be relaunched that way from the start.
- Do not pretend plain JS can replace trusted interactions on blocked pages.
- Do not promise `ljqCtrl` behavior from the zero-plugin browser path.
