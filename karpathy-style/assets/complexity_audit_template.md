# Complexity Audit

## Goal

- Target:
- Metric:
- Current result:

## Hot Path

- Main loop:
- Operations inside it:
- Values that can be precomputed or reused:
- Setup-only code that should not be optimized:

## Will Not Add

- New config surface:
- New dependency:
- Factory/plugin layer:
- Alternate backend:
- Persistence format:
- Generic abstraction:

## Complexity Ledger

| File | Added code | Why it exists | Delete if |
| --- | --- | --- | --- |

## Decision

Keep only if the metric improves, the bug is fixed, or the code becomes simpler without regression.
