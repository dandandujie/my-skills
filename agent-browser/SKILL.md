---
name: agent-browser
description: Use when the user wants GenericAgent-style browser automation without browser extensions. This skill uses a zero-plugin Chrome DevTools Protocol workflow through local scripts, keeps as much of the original TMWebDriver/CDP operating model as possible, and must not switch to Playwright, Selenium, or other replacements.
---

# Agent Browser

## Overview

This skill replaces the old extension bridge with local Chrome remote-debugging scripts.
Use the browser through `./scripts/cdpctl.sh` and `./scripts/launch-chrome-cdp.sh`.

The goal is still the same operating style as GenericAgent: real Chrome, real profile when needed, raw CDP when plain DOM work is not enough, and no Playwright.

## Start Here

- Run `./scripts/check-prereqs.sh`.
- First read [references/genericagent-setup.md](references/genericagent-setup.md).
- If the CDP endpoint is not up yet, start Chrome with `./scripts/launch-chrome-cdp.sh`.
- If the user needs their real logged-in browser state, tell them to relaunch their real Chrome profile with remote debugging instead of using the default temporary profile.
- Do not assume you can attach to an already-running Chrome that was not started with `--remote-debugging-port`.

## Tool Selection

- Use `./scripts/cdpctl.sh tabs` to discover targets.
- Use `./scripts/cdpctl.sh eval <target> "<js>"` for DOM reads, navigation, and small in-page actions.
- Use `./scripts/cdpctl.sh raw` or `batch` for low-level CDP methods.
- Use `./scripts/cdpctl.sh cookies`, `screenshot`, `click`, `type`, and `upload` before inventing ad hoc one-off scripts.
- Treat `ljqCtrl` as an external fallback only when browser-level automation is insufficient. This repository does not bundle `ljqCtrl`.

## Core Rules

- Do not import replacement browser frameworks for this skill.
- Stay on the zero-plugin CDP path. Do not tell the user to install `tmwd_cdp_bridge`.
- Prefer the highest-level local command that works: `tabs`, `eval`, `click`, `type`, `upload`, `cookies`, `screenshot`, then `raw` or `batch`.
- When a task needs the user's real login state, make the browser startup model explicit: close Chrome first if they want to relaunch an existing profile with remote debugging.
- Plain JS is still not trusted. If a site blocks synthetic DOM events, fall through to raw CDP methods such as `Input.dispatchMouseEvent`, `Input.insertText`, `DOM.setFileInputFiles`, or `Page.bringToFront`.
- Use `batch` for chained CDP operations that depend on earlier results, such as `DOM.getDocument` followed by `DOM.querySelector` and `DOM.setFileInputFiles`.
- For cross-origin iframe work, use raw CDP methods. Do not pretend same-page DOM helpers can see into those frames.
- If a task truly requires physical desktop input, say so plainly instead of pretending the zero-plugin browser path covers it.

## References

- Setup and troubleshooting: [references/genericagent-setup.md](references/genericagent-setup.md)
- Stack map: [references/source-mapping.md](references/source-mapping.md)
- Common workflows: [references/workflows.md](references/workflows.md)
