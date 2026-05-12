---
name: karpathy-style
description: Minimal, metric-driven software and research development in the spirit of Andrej Karpathy's nano projects. Use when building, refactoring, or guiding an AI coding agent to produce small, readable, high-leverage code with a fixed evaluation loop, narrow edit surface, experimental logs, rollback discipline, and strong resistance to speculative abstractions.
---

# Karpathy-Style Development

## Prime Directive

Turn the project into a small measurable world before writing clever code.

Prefer one complete working path over many configurable partial paths. Prefer a short explicit file over a flexible framework. Prefer deleting code with equal metrics over adding code with tiny gains.

## Operating Model

For every non-trivial task, define:

1. **Goal**: the concrete user-visible or metric-visible result.
2. **Metric**: the check that decides better/worse. Use tests, benchmark, validation loss, latency, memory, snapshot diff, or a small deterministic script.
3. **Baseline**: the current metric before changes, if feasible.
4. **Edit surface**: the smallest set of files the agent is allowed to touch.
5. **One knob**: the main complexity axis, if one exists. Collapse dependent choices into formulas or defaults instead of exposing config sprawl.

If no metric exists, first create the smallest honest proxy metric. Do not optimize by vibe.

## Taste Acquisition Loop

Taste is not a mood. Treat taste as compressed expert priors that predict which code will be simpler, faster, more stable, and easier to extend.

When domain intuition is missing, do not improvise from generic software patterns. Actively acquire priors:

1. Search the local repo first: implementation, tests, benchmark scripts, logs, issues, PRs, and commit history.
2. Search external sources when local evidence is thin: expert codebases, papers, benchmark writeups, design notes, postmortems, and high-signal discussions.
3. Prefer primary artifacts over summaries: source code, papers, benchmark tables, maintainer comments, reproducible experiments.
4. Distill sources into operational rules before coding.
5. Use those rules to reject ideas, not just generate ideas.

Convert research into compact prior cards:

```text
Prior: <short rule>
Evidence: <repo/paper/benchmark/source>
Applies when: <conditions>
Default: <constant/formula/pattern>
Avoid: <tempting but bad move>
Test: <metric/check that would falsify it>
```

Good priors look like: "batch size should scale with data horizon", "avoid wrapper-heavy code in per-token loops", "one depth knob derives width and heads", "evaluation must be tokenizer-independent".

Bad priors look like: "use best practices", "make it extensible", "modernize the architecture".

## Workflow

1. Read the critical path end to end: entrypoint, core data structures, scoring/tests, and output path.
2. State assumptions briefly. If the target is ambiguous, ask only for the ambiguity that blocks progress.
3. Build or identify the smallest runnable loop.
4. Make one surgical change.
5. Run the metric.
6. Keep the change only if it improves the metric, fixes the target bug, or removes complexity without regression.
7. Record the result when experimenting: commit/id, metric, status, memory/time if relevant, and a short description.
8. Repeat. Every few iterations, do a deletion pass.

For a new experiment repo, optionally run `scripts/init_experiment_ledger.py` to create `results.tsv`, `prior_cards.md`, and `complexity_audit.md`.

## Hot-Path Cost Model

Before changing performance-sensitive code, identify the hot path in plain terms:

- Which loop runs per token, per sample, per request, per frame, or per row?
- Which tensors, buffers, allocations, network calls, file reads, locks, regexes, serializers, or library wrappers sit inside that loop?
- Which values have fixed shapes and should be precomputed or reused?
- Which code runs once at setup and can be slightly clumsy without mattering?

Treat external libraries and convenience functions as suspicious inside hot paths. Use them when they buy hard correctness or a fast primitive; replace wrapper-heavy glue with direct code when the operation is simple, frequent, and measurable.

For each proposed hot-path change, write one sentence:

```text
This should be faster/smaller because it removes/reuses/hoists/fuses __________ from the __________ loop.
```

If that sentence is vague, do not make the performance change yet.

## Code Shape Rules

- Keep code local until duplication or complexity proves an abstraction is needed.
- Do not add factories, plugin systems, broad config objects, inheritance layers, or generic adapters for one use case.
- Encode expert defaults as simple formulas near their use site.
- Prefer a single readable script or module for a tight experiment harness.
- Keep comments for non-obvious reasoning, invariants, and empirical choices. Do not narrate syntax.
- Treat every branch, option, and dependency as cognitive debt.
- Use existing libraries for domain-hard primitives, but keep project glue minimal.
- Do not change the evaluation harness while trying to improve the score.

## Negative-Space Gate

Before adding code, explicitly decide what not to build.

Write a short "will not add" list for non-trivial changes:

```text
Will not add: new config surface, new dependency, factory layer, alternate backend, persistence format, generic plugin point.
```

Only remove an item from that list if the current task directly requires it and the metric or user value pays for it.

Default exclusions:

- no future-proofing without a second real use case,
- no generic abstraction for one caller,
- no new dependency for code that can be written clearly in a few local lines,
- no options that are not exercised by tests or examples,
- no cleanup outside the edit surface,
- no performance trick outside the measured hot path.

## Idea Taste Test

Before implementing a non-obvious idea, score it quickly:

```text
Idea: <one sentence>
Why it might work: <mechanism, not vibes>
Why it might be bad: <complexity/perf/stability risk>
Smallest test: <metric loop>
Deletion path: <how to revert/remove if wrong>
```

Prefer ideas with a clear mechanism, tiny diff, direct metric, and easy deletion.

## AI Failure Modes To Resist

- Adding knobs because they seem professional.
- Refactoring adjacent code to feel productive.
- Shipping unmeasured improvements.
- Over-generalizing before there are two real users of an abstraction.
- Replacing a short ugly-but-clear loop with a clever architecture.
- Hiding uncertainty in confident prose.
- Optimizing for passing review aesthetics instead of the metric.

## Experiment Log Format

For iterative optimization, keep a simple tab-separated log:

```text
id	metric	status	cost	description
baseline	1.234567	keep	0.0	current behavior
abc1234	1.220000	keep	+2%	compact targeted change
def5678	1.240000	discard	+0%	added complexity, worse metric
```

Status is `keep`, `discard`, or `crash`.

## Definition Of Done

A task is done only when:

- the main path runs,
- the metric/test result is reported,
- the diff is no larger than the problem demands,
- no speculative abstraction was added,
- any new complexity paid for itself in the metric or in clear user value.

Final responses should name the metric result and the smallest useful summary of the change.

## Bundled Resources

- `scripts/init_experiment_ledger.py`: initialize a metric ledger, prior-card file, and complexity audit file in a project.
- `references/prior_cards.md`: read when domain intuition is thin and expert priors must be acquired from code, papers, benchmarks, or discussions.
- `assets/complexity_audit_template.md`: copy or adapt when a project needs a recurring deletion/complexity review.
