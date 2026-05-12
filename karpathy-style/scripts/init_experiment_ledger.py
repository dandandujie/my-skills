#!/usr/bin/env python3
"""Initialize lightweight experiment files for Karpathy-style development."""

from __future__ import annotations

import argparse
from pathlib import Path


RESULTS_TEMPLATE = """id\tmetric\tstatus\tcost\tdescription
baseline\t\tkeep\t\tcurrent behavior
"""

PRIORS_TEMPLATE = """# Prior Cards

Use one card per acquired expert prior. Keep cards short enough to affect code decisions.

```text
Prior: <short rule>
Evidence: <repo/paper/benchmark/source>
Applies when: <conditions>
Default: <constant/formula/pattern>
Avoid: <tempting but bad move>
Test: <metric/check that would falsify it>
```
"""

AUDIT_TEMPLATE = """# Complexity Audit

Run this after several iterations or before finalizing a larger change.

## Hot Path

- Main loop:
- Costly operations inside it:
- Hoisted/reused/fused:

## Will Not Add

- New config surface:
- New dependency:
- Factory/plugin layer:
- Alternate backend:
- Generic abstraction:

## Lines That Must Earn Their Place

| File | Code | Why it exists | Delete if |
| --- | --- | --- | --- |
"""


def write_if_allowed(path: Path, content: str, force: bool) -> str:
    if path.exists() and not force:
        return f"skip {path} (exists)"
    path.write_text(content, encoding="utf-8")
    return f"write {path}"


def main() -> None:
    parser = argparse.ArgumentParser(description="Initialize Karpathy-style experiment files.")
    parser.add_argument("--dir", default=".", help="Target project directory.")
    parser.add_argument("--force", action="store_true", help="Overwrite existing files.")
    args = parser.parse_args()

    root = Path(args.dir).resolve()
    root.mkdir(parents=True, exist_ok=True)

    outputs = [
        write_if_allowed(root / "results.tsv", RESULTS_TEMPLATE, args.force),
        write_if_allowed(root / "prior_cards.md", PRIORS_TEMPLATE, args.force),
        write_if_allowed(root / "complexity_audit.md", AUDIT_TEMPLATE, args.force),
    ]
    for line in outputs:
        print(line)


if __name__ == "__main__":
    main()
