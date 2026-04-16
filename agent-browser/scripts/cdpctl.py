#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import socket
import ssl
import struct
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


DEFAULT_HOST = os.getenv("AGENT_BROWSER_CDP_HOST", "127.0.0.1")
DEFAULT_PORT = int(os.getenv("AGENT_BROWSER_CDP_PORT", "9222"))
DEFAULT_TIMEOUT = float(os.getenv("AGENT_BROWSER_CDP_TIMEOUT", "10"))


def die(message: str) -> "NoReturn":
    raise SystemExit(message)


def print_json(data: Any) -> None:
    json.dump(data, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")


def parse_json_arg(text: str | None, default: Any) -> Any:
    if text is None:
        return default
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        die(f"Invalid JSON: {exc}")


class ChromeHTTP:
    def __init__(self, host: str, port: int, timeout: float) -> None:
        self.host = host
        self.port = port
        self.timeout = timeout
        self.opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))

    def _url(self, path: str) -> str:
        return f"http://{self.host}:{self.port}{path}"

    def _decode_response(self, response: Any) -> Any:
        raw = response.read().decode("utf-8")
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return raw

    def _http_error_message(self, path: str, exc: urllib.error.HTTPError) -> str:
        detail = exc.read().decode("utf-8", "replace").strip()
        message = f"CDP request failed at {self._url(path)}: HTTP {exc.code} {exc.reason}"
        if detail:
            message += f": {detail}"
        return message

    def _request(self, path: str, *, method: str = "GET") -> Any:
        request = urllib.request.Request(self._url(path), method=method)
        try:
            with self.opener.open(request, timeout=self.timeout) as response:
                return self._decode_response(response)
        except urllib.error.HTTPError:
            raise
        except OSError as exc:
            die(f"CDP endpoint is not reachable at {self._url(path)}: {exc}")

    def _fetch(self, path: str, *, method: str = "GET") -> Any:
        try:
            return self._request(path, method=method)
        except urllib.error.HTTPError as exc:
            die(self._http_error_message(path, exc))

    def version(self) -> Any:
        return self._fetch("/json/version")

    def list_tabs(self) -> list[dict[str, Any]]:
        tabs = self._fetch("/json/list")
        if not isinstance(tabs, list):
            die("Unexpected /json/list response.")
        return [tab for tab in tabs if tab.get("type") == "page" and tab.get("webSocketDebuggerUrl")]

    def open(self, url: str) -> Any:
        encoded = urllib.parse.quote(url, safe=":/?&=%#")
        path = f"/json/new?{encoded}"
        try:
            return self._request(path, method="PUT")
        except urllib.error.HTTPError as exc:
            if exc.code != 405:
                die(self._http_error_message(path, exc))
        return self._fetch(path)

    def activate(self, target_id: str) -> Any:
        return self._fetch(f"/json/activate/{target_id}")

    def close(self, target_id: str) -> Any:
        return self._fetch(f"/json/close/{target_id}")

    def resolve_tab(self, selector: str | None) -> dict[str, Any]:
        tabs = self.list_tabs()
        if selector in (None, ""):
            if len(tabs) == 1:
                return tabs[0]
            die(f"Target is required because {len(tabs)} page targets are open.")

        exact = [tab for tab in tabs if tab.get("id") == selector]
        if exact:
            return exact[0]

        needle = selector.lower()
        matches = [
            tab
            for tab in tabs
            if needle in tab.get("url", "").lower() or needle in tab.get("title", "").lower()
        ]
        if not matches:
            die(f"No page target matched '{selector}'. Run `./scripts/cdpctl.sh tabs` first.")
        if len(matches) > 1:
            summary = [{"id": tab["id"], "title": tab.get("title", ""), "url": tab.get("url", "")} for tab in matches]
            die("Target selector is ambiguous:\n" + json.dumps(summary, ensure_ascii=False, indent=2))
        return matches[0]


class WebSocketClient:
    def __init__(self, ws_url: str, timeout: float) -> None:
        self.ws_url = ws_url
        self.timeout = timeout
        self.sock = self._connect()

    def _connect(self) -> socket.socket:
        parsed = urllib.parse.urlparse(self.ws_url)
        host = parsed.hostname or die(f"Invalid websocket URL: {self.ws_url}")
        port = parsed.port or (443 if parsed.scheme == "wss" else 80)
        path = parsed.path or "/"
        if parsed.query:
            path += f"?{parsed.query}"

        raw_sock = socket.create_connection((host, port), timeout=self.timeout)
        if parsed.scheme == "wss":
            context = ssl.create_default_context()
            sock = context.wrap_socket(raw_sock, server_hostname=host)
        else:
            sock = raw_sock

        key = base64.b64encode(os.urandom(16)).decode("ascii")
        request = (
            f"GET {path} HTTP/1.1\r\n"
            f"Host: {host}:{port}\r\n"
            "Upgrade: websocket\r\n"
            "Connection: Upgrade\r\n"
            f"Sec-WebSocket-Key: {key}\r\n"
            "Sec-WebSocket-Version: 13\r\n"
            "\r\n"
        )
        sock.sendall(request.encode("ascii"))

        response = b""
        while b"\r\n\r\n" not in response:
            chunk = sock.recv(4096)
            if not chunk:
                die("WebSocket handshake failed: connection closed.")
            response += chunk

        header_text = response.split(b"\r\n\r\n", 1)[0].decode("utf-8", "replace")
        lines = header_text.split("\r\n")
        if not lines or "101" not in lines[0]:
            die(f"WebSocket handshake failed: {lines[0] if lines else header_text}")

        headers: dict[str, str] = {}
        for line in lines[1:]:
            if ":" in line:
                name, value = line.split(":", 1)
                headers[name.strip().lower()] = value.strip()

        expected = base64.b64encode(
            hashlib.sha1((key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11").encode("ascii")).digest()
        ).decode("ascii")
        if headers.get("sec-websocket-accept") != expected:
            die("WebSocket handshake failed: invalid accept header.")
        return sock

    def _read_exact(self, size: int) -> bytes:
        buffer = bytearray()
        while len(buffer) < size:
            chunk = self.sock.recv(size - len(buffer))
            if not chunk:
                die("WebSocket connection closed unexpectedly.")
            buffer.extend(chunk)
        return bytes(buffer)

    def _send_frame(self, opcode: int, payload: bytes = b"") -> None:
        first = 0x80 | opcode
        length = len(payload)
        mask_key = os.urandom(4)

        if length < 126:
            header = bytes([first, 0x80 | length])
        elif length < 65536:
            header = bytes([first, 0x80 | 126]) + struct.pack("!H", length)
        else:
            header = bytes([first, 0x80 | 127]) + struct.pack("!Q", length)

        masked = bytes(byte ^ mask_key[index % 4] for index, byte in enumerate(payload))
        self.sock.sendall(header + mask_key + masked)

    def send_text(self, text: str) -> None:
        self._send_frame(0x1, text.encode("utf-8"))

    def recv_text(self) -> str | None:
        fragments: list[bytes] = []
        while True:
            head = self._read_exact(2)
            first, second = head[0], head[1]
            opcode = first & 0x0F
            masked = bool(second & 0x80)
            length = second & 0x7F

            if length == 126:
                length = struct.unpack("!H", self._read_exact(2))[0]
            elif length == 127:
                length = struct.unpack("!Q", self._read_exact(8))[0]

            mask_key = self._read_exact(4) if masked else b""
            payload = self._read_exact(length)
            if masked:
                payload = bytes(byte ^ mask_key[index % 4] for index, byte in enumerate(payload))

            if opcode == 0x8:
                return None
            if opcode == 0x9:
                self._send_frame(0xA, payload)
                continue
            if opcode == 0xA:
                continue
            if opcode in (0x0, 0x1):
                fragments.append(payload)
                if first & 0x80:
                    return b"".join(fragments).decode("utf-8")
                continue
            die(f"Unsupported websocket opcode: {opcode}")

    def close(self) -> None:
        try:
            self._send_frame(0x8)
        except OSError:
            pass
        try:
            self.sock.close()
        except OSError:
            pass


class CDPSession:
    def __init__(self, ws_url: str, timeout: float) -> None:
        self.ws = WebSocketClient(ws_url, timeout)
        self.next_id = 0
        self.enabled_domains: set[str] = set()

    def close(self) -> None:
        self.ws.close()

    def enable(self, domain: str) -> None:
        if domain in self.enabled_domains:
            return
        try:
            self.call(f"{domain}.enable")
        except SystemExit:
            raise
        except Exception:
            return
        self.enabled_domains.add(domain)

    def call(self, method: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        self.next_id += 1
        request_id = self.next_id
        message = {"id": request_id, "method": method}
        if params is not None:
            message["params"] = params
        self.ws.send_text(json.dumps(message))

        while True:
            raw = self.ws.recv_text()
            if raw is None:
                die("CDP websocket closed before a response arrived.")
            payload = json.loads(raw)
            if payload.get("id") != request_id:
                continue
            if "error" in payload:
                error = payload["error"]
                die(f"{method} failed: {error.get('message', error)}")
            return payload.get("result", {})

    def evaluate(self, expression: str, *, await_promise: bool = True, return_by_value: bool = True) -> Any:
        self.enable("Runtime")
        result = self.call(
            "Runtime.evaluate",
            {
                "expression": expression,
                "awaitPromise": await_promise,
                "returnByValue": return_by_value,
            },
        )
        if "exceptionDetails" in result:
            detail = result["exceptionDetails"]
            message = detail.get("exception", {}).get("description") or detail.get("text") or "JavaScript evaluation failed."
            die(message)
        remote = result.get("result", {})
        if return_by_value:
            if "value" in remote:
                return remote["value"]
            if "unserializableValue" in remote:
                return remote["unserializableValue"]
        return remote


def with_target(args: argparse.Namespace) -> tuple[dict[str, Any], CDPSession]:
    chrome = ChromeHTTP(args.host, args.port, args.timeout)
    tab = chrome.resolve_tab(args.target)
    return tab, CDPSession(tab["webSocketDebuggerUrl"], args.timeout)


def selector_center_expression(selector: str) -> str:
    quoted = json.dumps(selector)
    return (
        "(async () => {"
        f"const selector = {quoted};"
        "const el = document.querySelector(selector);"
        "if (!el) throw new Error(`Selector not found: ${selector}`);"
        "el.scrollIntoView({block:'center', inline:'center'});"
        "await new Promise(resolve => setTimeout(resolve, 50));"
        "const rect = el.getBoundingClientRect();"
        "return {x: rect.left + rect.width / 2, y: rect.top + rect.height / 2};"
        "})()"
    )


def dispatch_click(cdp: CDPSession, x: float, y: float) -> None:
    cdp.call("Input.dispatchMouseEvent", {"type": "mouseMoved", "x": x, "y": y, "button": "none"})
    cdp.call("Input.dispatchMouseEvent", {"type": "mousePressed", "x": x, "y": y, "button": "left", "clickCount": 1})
    cdp.call("Input.dispatchMouseEvent", {"type": "mouseReleased", "x": x, "y": y, "button": "left", "clickCount": 1})


def resolve_references(value: Any, results: list[Any]) -> Any:
    if isinstance(value, str) and value.startswith("$"):
        index_text, _, path = value[1:].partition(".")
        try:
            resolved: Any = results[int(index_text)]
        except (ValueError, IndexError):
            die(f"Invalid batch reference: {value}")
        if path:
            for part in path.split("."):
                if isinstance(resolved, list):
                    resolved = resolved[int(part)]
                else:
                    resolved = resolved[part]
        return resolved
    if isinstance(value, list):
        return [resolve_references(item, results) for item in value]
    if isinstance(value, dict):
        return {key: resolve_references(item, results) for key, item in value.items()}
    return value


def command_version(args: argparse.Namespace) -> None:
    chrome = ChromeHTTP(args.host, args.port, args.timeout)
    print_json(chrome.version())


def command_tabs(args: argparse.Namespace) -> None:
    chrome = ChromeHTTP(args.host, args.port, args.timeout)
    tabs = [
        {"id": tab["id"], "title": tab.get("title", ""), "url": tab.get("url", "")}
        for tab in chrome.list_tabs()
    ]
    print_json(tabs)


def command_open(args: argparse.Namespace) -> None:
    chrome = ChromeHTTP(args.host, args.port, args.timeout)
    print_json(chrome.open(args.url))


def command_activate(args: argparse.Namespace) -> None:
    chrome = ChromeHTTP(args.host, args.port, args.timeout)
    tab = chrome.resolve_tab(args.target)
    chrome.activate(tab["id"])
    print_json({"ok": True, "id": tab["id"], "title": tab.get("title", ""), "url": tab.get("url", "")})


def command_close(args: argparse.Namespace) -> None:
    chrome = ChromeHTTP(args.host, args.port, args.timeout)
    tab = chrome.resolve_tab(args.target)
    chrome.close(tab["id"])
    print_json({"ok": True, "id": tab["id"], "title": tab.get("title", ""), "url": tab.get("url", "")})


def command_eval(args: argparse.Namespace) -> None:
    tab, cdp = with_target(args)
    try:
        value = cdp.evaluate(args.expression, await_promise=not args.no_await, return_by_value=not args.remote_object)
    finally:
        cdp.close()
    print_json({"target": {"id": tab["id"], "url": tab.get("url", ""), "title": tab.get("title", "")}, "value": value})


def command_navigate(args: argparse.Namespace) -> None:
    tab, cdp = with_target(args)
    try:
        cdp.enable("Page")
        result = cdp.call("Page.navigate", {"url": args.url})
    finally:
        cdp.close()
    print_json({"target": {"id": tab["id"], "url": tab.get("url", ""), "title": tab.get("title", "")}, "result": result})


def command_raw(args: argparse.Namespace) -> None:
    params = parse_json_arg(args.params, {})
    tab, cdp = with_target(args)
    try:
        domain = args.method.split(".", 1)[0]
        if domain in {"DOM", "Network", "Page", "Runtime"}:
            cdp.enable(domain)
        result = cdp.call(args.method, params)
    finally:
        cdp.close()
    print_json({"target": {"id": tab["id"], "url": tab.get("url", ""), "title": tab.get("title", "")}, "result": result})


def command_batch(args: argparse.Namespace) -> None:
    commands = parse_json_arg(args.json, None)
    if commands is None and args.file:
        try:
            commands = json.loads(Path(args.file).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            die(f"Failed to load batch file: {exc}")
    if not isinstance(commands, list):
        die("Batch input must be a JSON array.")

    tab, cdp = with_target(args)
    results: list[Any] = []
    try:
        for command in commands:
            method = command.get("method")
            if not method:
                die("Each batch command requires a 'method'.")
            params = resolve_references(command.get("params", {}), results)
            domain = method.split(".", 1)[0]
            if domain in {"DOM", "Network", "Page", "Runtime"}:
                cdp.enable(domain)
            results.append(cdp.call(method, params))
    finally:
        cdp.close()
    print_json({"target": {"id": tab["id"], "url": tab.get("url", ""), "title": tab.get("title", "")}, "results": results})


def command_screenshot(args: argparse.Namespace) -> None:
    tab, cdp = with_target(args)
    try:
        cdp.enable("Page")
        result = cdp.call("Page.captureScreenshot", {"format": args.format})
    finally:
        cdp.close()

    output_path = Path(args.output or f"screenshot-{tab['id'][:8]}.{args.format}").expanduser().resolve()
    image = base64.b64decode(result["data"])
    output_path.write_bytes(image)
    print_json({"ok": True, "path": str(output_path), "bytes": len(image)})


def command_cookies(args: argparse.Namespace) -> None:
    tab, cdp = with_target(args)
    try:
        cdp.enable("Network")
        params = {}
        if tab.get("url", "").startswith(("http://", "https://")):
            params["urls"] = [tab["url"]]
        result = cdp.call("Network.getCookies", params)
    finally:
        cdp.close()
    print_json({"target": {"id": tab["id"], "url": tab.get("url", ""), "title": tab.get("title", "")}, "cookies": result.get("cookies", [])})


def command_click(args: argparse.Namespace) -> None:
    tab, cdp = with_target(args)
    try:
        cdp.enable("Runtime")
        cdp.enable("Page")
        coords = cdp.evaluate(selector_center_expression(args.selector))
        dispatch_click(cdp, coords["x"], coords["y"])
    finally:
        cdp.close()
    print_json({"ok": True, "target": {"id": tab["id"], "url": tab.get("url", ""), "title": tab.get("title", "")}, "selector": args.selector})


def command_type(args: argparse.Namespace) -> None:
    tab, cdp = with_target(args)
    try:
        cdp.enable("Runtime")
        cdp.enable("Page")
        coords = cdp.evaluate(selector_center_expression(args.selector))
        dispatch_click(cdp, coords["x"], coords["y"])
        if args.clear:
            cdp.evaluate(
                "(selector => {"
                "const el = document.querySelector(selector);"
                "if (!el) throw new Error(`Selector not found: ${selector}`);"
                "el.value = '';"
                "el.dispatchEvent(new Event('input', {bubbles: true}));"
                "el.dispatchEvent(new Event('change', {bubbles: true}));"
                f"}})({json.dumps(args.selector)})"
            )
        cdp.call("Input.insertText", {"text": args.text})
        if not args.no_events:
            cdp.evaluate(
                "(() => {"
                "const el = document.activeElement;"
                "if (el) {"
                "el.dispatchEvent(new Event('input', {bubbles: true}));"
                "el.dispatchEvent(new Event('change', {bubbles: true}));"
                "}"
                "return true;"
                "})()"
            )
    finally:
        cdp.close()
    print_json({"ok": True, "target": {"id": tab["id"], "url": tab.get("url", ""), "title": tab.get("title", "")}, "selector": args.selector})


def command_upload(args: argparse.Namespace) -> None:
    files = [str(Path(file_path).expanduser().resolve()) for file_path in args.files]
    missing = [file_path for file_path in files if not Path(file_path).exists()]
    if missing:
        die("Missing upload files:\n" + "\n".join(missing))

    tab, cdp = with_target(args)
    try:
        cdp.enable("DOM")
        root = cdp.call("DOM.getDocument", {"depth": 1, "pierce": True})
        node = cdp.call("DOM.querySelector", {"nodeId": root["root"]["nodeId"], "selector": args.selector})
        if not node.get("nodeId"):
            die(f"Selector not found for upload: {args.selector}")
        cdp.call("DOM.setFileInputFiles", {"nodeId": node["nodeId"], "files": files})
        if not args.no_events:
            cdp.evaluate(
                "(selector => {"
                "const el = document.querySelector(selector);"
                "if (!el) throw new Error(`Selector not found: ${selector}`);"
                "el.dispatchEvent(new Event('input', {bubbles: true}));"
                "el.dispatchEvent(new Event('change', {bubbles: true}));"
                f"}})({json.dumps(args.selector)})"
            )
    finally:
        cdp.close()
    print_json({"ok": True, "target": {"id": tab["id"], "url": tab.get("url", ""), "title": tab.get("title", "")}, "selector": args.selector, "files": files})


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Zero-plugin Chrome CDP control for agent-browser.")
    parser.add_argument("--host", default=DEFAULT_HOST, help="CDP host. Defaults to %(default)s.")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="CDP port. Defaults to %(default)s.")
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT, help="Socket timeout in seconds.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    version_parser = subparsers.add_parser("version", help="Show Chrome CDP endpoint metadata.")
    version_parser.set_defaults(func=command_version)

    tabs_parser = subparsers.add_parser("tabs", help="List page targets.")
    tabs_parser.set_defaults(func=command_tabs)

    open_parser = subparsers.add_parser("open", help="Open a new tab.")
    open_parser.add_argument("url")
    open_parser.set_defaults(func=command_open)

    activate_parser = subparsers.add_parser("activate", help="Activate a target tab.")
    activate_parser.add_argument("target")
    activate_parser.set_defaults(func=command_activate)

    close_parser = subparsers.add_parser("close", help="Close a target tab.")
    close_parser.add_argument("target")
    close_parser.set_defaults(func=command_close)

    eval_parser = subparsers.add_parser("eval", help="Evaluate JavaScript in a target tab.")
    eval_parser.add_argument("target")
    eval_parser.add_argument("expression")
    eval_parser.add_argument("--no-await", action="store_true", help="Do not await returned promises.")
    eval_parser.add_argument("--remote-object", action="store_true", help="Return the raw remote object instead of by-value data.")
    eval_parser.set_defaults(func=command_eval)

    navigate_parser = subparsers.add_parser("navigate", help="Navigate a target tab to a URL.")
    navigate_parser.add_argument("target")
    navigate_parser.add_argument("url")
    navigate_parser.set_defaults(func=command_navigate)

    raw_parser = subparsers.add_parser("raw", help="Send a raw CDP method call.")
    raw_parser.add_argument("target")
    raw_parser.add_argument("method")
    raw_parser.add_argument("--params", help="JSON object of CDP params.")
    raw_parser.set_defaults(func=command_raw)

    batch_parser = subparsers.add_parser("batch", help="Run a batch of raw CDP method calls.")
    batch_parser.add_argument("target")
    batch_source = batch_parser.add_mutually_exclusive_group(required=True)
    batch_source.add_argument("--json", help="Inline JSON array of batch commands.")
    batch_source.add_argument("--file", help="Path to a JSON file containing batch commands.")
    batch_parser.set_defaults(func=command_batch)

    screenshot_parser = subparsers.add_parser("screenshot", help="Capture a screenshot from a target tab.")
    screenshot_parser.add_argument("target")
    screenshot_parser.add_argument("--output", help="Output file path.")
    screenshot_parser.add_argument("--format", default="png", choices=["png", "jpeg", "webp"])
    screenshot_parser.set_defaults(func=command_screenshot)

    cookies_parser = subparsers.add_parser("cookies", help="Read cookies for a target tab.")
    cookies_parser.add_argument("target")
    cookies_parser.set_defaults(func=command_cookies)

    click_parser = subparsers.add_parser("click", help="Click a selector through CDP mouse events.")
    click_parser.add_argument("target")
    click_parser.add_argument("selector")
    click_parser.set_defaults(func=command_click)

    type_parser = subparsers.add_parser("type", help="Focus a selector and type text through CDP.")
    type_parser.add_argument("target")
    type_parser.add_argument("selector")
    type_parser.add_argument("text")
    type_parser.add_argument("--clear", action="store_true", help="Clear the field before typing.")
    type_parser.add_argument("--no-events", action="store_true", help="Skip follow-up input/change events.")
    type_parser.set_defaults(func=command_type)

    upload_parser = subparsers.add_parser("upload", help="Set files on an input[type=file] selector.")
    upload_parser.add_argument("target")
    upload_parser.add_argument("selector")
    upload_parser.add_argument("files", nargs="+")
    upload_parser.add_argument("--no-events", action="store_true", help="Skip follow-up input/change events.")
    upload_parser.set_defaults(func=command_upload)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
