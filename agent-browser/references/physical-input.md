# ljqCtrl Physical Input

Use when JS/CDP can't work: isTrusted-required events, native file dialogs, desktop app interaction.

## API Reference

```python
import sys, os, pygetwindow as gw
sys.path.append("../memory")
import ljqCtrl
```

| API | Description |
|-----|-------------|
| `ljqCtrl.dpi_scale` | float — scale factor = logical / physical width |
| `ljqCtrl.Click(x, y)` | Click at physical coords. Also accepts `Click((x, y))` |
| `ljqCtrl.SetCursorPos((x, y))` | Move mouse to logical coords |
| `ljqCtrl.Press('ctrl+c')` | Simulate key combo |
| `ljqCtrl.MouseDClick(staytime=0.05)` | Double-click at current position |
| `ljqCtrl.FindBlock(fn, wrect=None, threshold=0.8)` | Template match. Returns `((cx, cy), found)` |

## Core Rule: Physical Coordinates

**ljqCtrl.Click/SetCursorPos accept physical pixel coordinates (= screenshot pixel coordinates).**

Conversion from logical (pygetwindow, win32gui):
```
physical_coord = logical_coord / ljqCtrl.dpi_scale
```

All relative offsets (e.g., "move 10px right") also need `/ dpi_scale`.

## Workflow

1. **Activate window** (mandatory before any click):
   ```python
   win = gw.getWindowsWithTitle('Window Title')[0]
   win.restore()
   win.activate()
   ```

2. **Calculate and click**:
   ```python
   # lx, ly = logical coordinates from pygetwindow
   px = lx / ljqCtrl.dpi_scale
   py = ly / ljqCtrl.dpi_scale
   ljqCtrl.Click(px, py)
   ```

3. **Text input** (no TypeText API):
   ```python
   ljqCtrl.Click(field_x, field_y)  # focus field
   ljqCtrl.Press('ctrl+a')           # select all
   import pyperclip
   pyperclip.copy('text to type')
   ljqCtrl.Press('ctrl+v')           # paste
   ```

## Coordinate Pitfalls

### pygetwindow -> physical
pygetwindow returns logical coordinates. Always `/ dpi_scale` before passing to ljqCtrl.

### GetWindowRect vs ClientToScreen
`win32gui.GetWindowRect(hwnd)` includes title bar + borders. Screenshot content is client area only.

**Correct**: Use `win32gui.ClientToScreen(hwnd, (0, 0))` for client area origin, then add screenshot offset.
**Wrong**: GetWindowRect top-left + screenshot coords (off by title bar height).

### DPI Awareness
Without `SetProcessDPIAware()`, all win32 APIs (`GetWindowRect`, `ClientToScreen`, `GetClientRect`) return **logical** coordinates. If screenshot/ljqCtrl uses physical pixels, must `/ dpi_scale`.

Alternative: call `SetProcessDPIAware()` first, then everything is raw physical — never mix logical and physical.

### DOMRect Pitfall
Some contexts return `rect.x/y` as undefined (only `left/top` exist). Always use `rect.x ?? rect.left` to avoid NaN in overlap calculations.

## JS-to-Physical Coordinate Bridge

When converting browser element coords to physical screen coords for ljqCtrl:
```
physX = (screenX + rect_center_x) * dpr
physY = (screenY + chromeH + rect_center_y) * dpr
```
Where `chromeH = outerHeight - innerHeight` (browser chrome height).
