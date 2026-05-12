# Prior Cards

Use this reference when domain intuition is missing. The goal is to turn search results and expert artifacts into compact rules that affect code.

## Source Quality

Prefer:

- local source code, tests, benchmark scripts, and commit history,
- primary papers and benchmark tables,
- maintainer comments, design docs, and postmortems,
- reproducible experiment logs.

Avoid:

- generic "best practices" lists,
- unsourced summaries,
- advice that cannot be falsified by a project metric.

## Card Template

```text
Prior: <short rule>
Evidence: <repo/paper/benchmark/source>
Applies when: <conditions>
Default: <constant/formula/pattern>
Avoid: <tempting but bad move>
Test: <metric/check that would falsify it>
```

## Example Cards

```text
Prior: Avoid wrapper-heavy glue inside per-token or per-step loops.
Evidence: nano-style training loops preallocate buffers, fuse optimizer steps, and keep shapes static.
Applies when: training/inference hot paths run thousands of times.
Default: hoist allocation, reuse buffers, fuse small ops, keep shapes fixed.
Avoid: generic collators, dynamic dispatch, repeated serialization, and hidden tensor copies in hot loops.
Test: step time, tok/sec, MFU, peak memory.
```

```text
Prior: Collapse model complexity into one main knob when a scaling axis exists.
Evidence: nanochat derives width, heads, batch, horizon, and schedules from depth and scaling assumptions.
Applies when: users need a family of related models or experiments.
Default: expose the primary axis; derive secondary settings with local formulas.
Avoid: large config surfaces with many independent knobs.
Test: sweep the knob and verify the derived settings remain valid.
```
