#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import sys
from pathlib import Path


START = "<!-- LLM-WIKI:START -->"
END = "<!-- LLM-WIKI:END -->"
IGNORED_NEW_PROJECT_NAMES = {
    ".DS_Store",
    ".git",
    ".gitignore",
    ".hg",
    ".llm-wiki",
    ".svn",
    "__pycache__",
    "build",
    "dist",
    "node_modules",
}


def today() -> str:
    return dt.date.today().isoformat()


def write_file(path: Path, content: str, dry_run: bool) -> str:
    if path.exists():
        return f"skip existing {path}"
    if not dry_run:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    return f"create {path}"


def has_meaningful_project_files(target: Path) -> bool:
    if not target.exists():
        return False
    return any(path.name not in IGNORED_NEW_PROJECT_NAMES for path in target.iterdir())


def replace_managed_block(text: str, block: str, path: Path) -> str:
    has_start = START in text
    has_end = END in text
    if has_start != has_end:
        raise ValueError(f"{path} has only one LLM-WIKI marker")
    if has_start:
        start = text.index(START)
        end = text.index(END, start) + len(END)
        return text[:start].rstrip() + "\n\n" + block + "\n" + text[end:].lstrip()
    if text.strip():
        return text.rstrip() + "\n\n" + block + "\n"
    return f"# {path.stem}\n\n{block}\n"


def router_block(scope: str, wiki_dir: str) -> str:
    scope_label = "project" if scope == "project" else "global instruction set"
    return f"""{START}
## LLM Wiki Router

This {scope_label} uses `{wiki_dir}/` as the persistent knowledge layer. This file is only the router and lifecycle contract.

### Load Order

1. Read this router block.
2. Open `{wiki_dir}/index.md`.
3. Open only the route pages needed for the current task.
4. Verify important claims against source files before editing behavior.

### Routes

- `{wiki_dir}/index.md`: route table, freshness status, current context budget.
- `{wiki_dir}/project-map.md`: codebase layout, module ownership, boundaries, important entry points.
- `{wiki_dir}/workflows.md`: setup, test, build, release, debugging, and repeated operational commands.
- `{wiki_dir}/decisions.md`: architectural decisions, constraints, rejected alternatives, and rationale.
- `{wiki_dir}/glossary.md`: project vocabulary, domain terms, acronyms, and naming conventions.
- `{wiki_dir}/open-questions.md`: unknowns, stale assumptions, blocked investigations, and required confirmations.
- `{wiki_dir}/task-log.md`: notable agent work, changed files, verification, and follow-up context.

### Lifecycle Rules

- Before work: load only the wiki pages relevant to the request.
- During work: update wiki pages when code structure, commands, contracts, dependencies, decisions, or risks change.
- After work: update `task-log.md`; update `index.md` if routes, freshness, or open questions changed.
- Do not duplicate long facts in this router. Link to the canonical wiki page.
- If wiki content conflicts with source code, source code wins; update the wiki immediately.
<!-- LLM-WIKI:END -->"""


def page_templates(project_name: str, scope: str) -> dict[str, str]:
    date = today()
    return {
        "index.md": f"""# LLM Wiki Index

- name: {project_name}
- scope: {scope}
- last_reviewed: {date}
- source_of_truth: router files plus verified project/global sources
- update_trigger: routes, freshness, invariants, or open questions change

## Context Budget

- default_load: router + this file
- task_load_rule: open the smallest route set that can answer the current request

## Route Table

| Need | Open | Notes |
| --- | --- | --- |
| Code or knowledge layout | `project-map.md` | Entry points, boundaries, ownership |
| Setup or repeated commands | `workflows.md` | Test, build, run, debug |
| Durable technical choices | `decisions.md` | Accepted and superseded decisions |
| Terms and naming | `glossary.md` | Domain vocabulary |
| Uncertainty | `open-questions.md` | Unknowns that affect work |
| Recent agent work | `task-log.md` | Changes, verification, residual risk |

## Freshness

| Page | Last reviewed | Risk | Next review trigger |
| --- | --- | --- | --- |
| `project-map.md` | {date} | unknown | source layout changes |
| `workflows.md` | {date} | unknown | commands or dependencies change |
| `decisions.md` | {date} | unknown | durable choices change |
| `glossary.md` | {date} | unknown | naming or domain terms change |
| `open-questions.md` | {date} | unknown | questions are answered or added |
| `task-log.md` | {date} | low | notable work completes |

## Current Invariants

- Keep router files compact; compiled knowledge belongs in `.llm-wiki/`.

## Open Questions Snapshot

- Fill after the first evidence-backed audit.
""",
        "project-map.md": f"""# Project Map

- scope: {scope}
- last_reviewed: {date}
- source_of_truth: source tree, README, tests, package/build config
- update_trigger: directories, entry points, module boundaries, public APIs, or generated artifacts change

## Directory Map

- Fill from repository evidence.

## Entry Points

- Fill from source files and package/build configuration.

## Boundaries

- Fill with module ownership, public contracts, and files agents should avoid editing manually.

## Evidence

- Add file paths or command outputs that support this map.
""",
        "workflows.md": f"""# Workflows

- scope: {scope}
- last_reviewed: {date}
- source_of_truth: package scripts, Makefiles, CI config, docs, local verification
- update_trigger: setup, test, build, run, debug, env vars, ports, or services change

## Setup

- Fill after inspecting the project.

## Test

- Fill exact commands and expected scope.

## Build And Run

- Fill exact commands, required services, ports, and environment assumptions.

## Debugging

- Add repeated diagnostic commands and known failure modes.
""",
        "decisions.md": f"""# Decisions

- scope: {scope}
- last_reviewed: {date}
- source_of_truth: code, tests, docs, issue/PR notes, user decisions
- update_trigger: durable technical choices are made, reversed, or constrained by new evidence

## Template

### YYYY-MM-DD - Decision Title

- status: proposed | accepted | superseded
- context:
- decision:
- rationale:
- rejected_alternatives:
- consequences:
- evidence:
""",
        "glossary.md": f"""# Glossary

- scope: {scope}
- last_reviewed: {date}
- source_of_truth: code names, docs, domain sources, user terminology
- update_trigger: new project vocabulary, acronyms, aliases, or naming constraints appear

## Terms

| Term | Meaning | Evidence |
| --- | --- | --- |
""",
        "open-questions.md": f"""# Open Questions

- scope: {scope}
- last_reviewed: {date}
- source_of_truth: unanswered evidence checks and user confirmations
- update_trigger: uncertainty is found, answered, or starts blocking safe work

## Questions

### First Audit

- status: open
- why_it_matters: replace this with real unknowns after inspecting the project
- evidence_checked:
- owner_or_next_step:
- answer:
""",
        "task-log.md": f"""# Task Log

- scope: {scope}
- last_reviewed: {date}
- source_of_truth: completed agent work and verification results
- update_trigger: notable work completes or leaves follow-up context

## {date} - Bootstrap LLM Wiki

- request: initialize router-backed LLM Wiki
- changed: created wiki skeleton and router managed blocks
- verified: scaffold generated
- wiki_updates: initial pages created
- residual_risk: content still needs evidence-backed project audit
""",
        "raw/README.md": f"""# Raw Sources

Optional provenance store for source notes, pasted transcripts, meeting notes, or imported documents.

Do not load this directory by default. Promote durable facts into compiled wiki pages and cite the raw source filename.
""",
    }


def update_router_file(path: Path, block: str, dry_run: bool) -> str:
    original = path.read_text(encoding="utf-8") if path.exists() else ""
    updated = replace_managed_block(original, block, path)
    if updated == original:
        return f"unchanged {path}"
    if not dry_run:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(updated, encoding="utf-8")
    return f"update {path}"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Bootstrap a router-backed LLM Wiki in a project or global instruction directory."
    )
    parser.add_argument("target", nargs="?", default=".", help="Project or global instruction directory.")
    parser.add_argument("--scope", choices=["project", "global"], default="project")
    parser.add_argument("--wiki-dir", default=".llm-wiki")
    parser.add_argument(
        "--router-file",
        action="append",
        dest="router_files",
        help="Router filename to create/update. Repeat to target multiple files. Defaults to AGENTS.md and CLAUDE.md.",
    )
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    target = Path(args.target).expanduser().resolve()
    router_files = args.router_files or ["AGENTS.md", "CLAUDE.md"]
    project_name = target.name
    wiki_dir = args.wiki_dir.strip().rstrip("/")
    if not wiki_dir:
        print("--wiki-dir cannot be empty", file=sys.stderr)
        return 2

    existing_project = has_meaningful_project_files(target)
    results: list[str] = []
    for rel_path, content in page_templates(project_name, args.scope).items():
        results.append(write_file(target / wiki_dir / rel_path, content, args.dry_run))

    block = router_block(args.scope, wiki_dir)
    for router_file in router_files:
        results.append(update_router_file(target / router_file, block, args.dry_run))

    prefix = "dry-run " if args.dry_run else ""
    for result in results:
        print(prefix + result)
    if existing_project:
        print(
            "note: existing project files detected; this helper preserves/appends router blocks "
            "but does not replace the required project audit or evidence-backed wiki fill."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
