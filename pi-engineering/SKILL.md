---
name: pi-engineering
description: Evidence-driven project thinking and software engineering derived from Mario Zechner's broader work, the actual Pi codebase, and verified rewrites. Use proactively for defining a project's core philosophy, non-goals, architecture, or first vertical slice, and for non-trivial implementation, debugging, refactoring, or review where ownership, abstractions, state, dependencies, or correctness matter. Especially use when an AI may turn a wishlist into architecture, over-engineer, copy adjacent code, add defensive machinery, or claim completion after partial checks. Applies across languages, repositories, tools, operating systems, and agent harnesses.
compatibility: Requires only project inspection and, when available, the project's own checks. No Pi-specific tools or dependencies.
---

# Pi Engineering Discipline

Transfer the verified engineering decisions, not Mario's personality, prose, identifiers, concrete keybindings/UI choices, or known bugs. Current repository requirements determine product semantics; historical Pi examples only illuminate ownership and trade-offs.

## Objective

Minimize **independent mechanisms, state combinations, and error owners**, not raw line count.

Direct code is preferred only after understanding the real flow. A short patch in the wrong layer is worse than a larger change that restores one clear owner.

For a small, precise task, use this file alone. Before the first edit, load **at most one** reference, only when the named decision is active:

- new project, broad feature set, or unclear governing idea → [project-loop](references/project-loop.md)
- function/type/UI/CLI/persistence shape → [code-shapes](references/code-shapes.md)
- async state, streams, queues, terminals, destructive I/O → [state-and-boundaries](references/state-and-boundaries.md)
- ambiguous ownership in an existing codebase → [real-rewrites](references/real-rewrites.md)

Use [review-checklist](references/review-checklist.md) only after implementation when the diff is high-risk or crosses owners. Never load historical rewrites merely to choose a key, label, limit, or interaction for the current product.

For a new project or broad feature, keep one feedback loop: `real friction → product gestalt/non-goals → owner map → thinnest real vertical slice → implementation evidence → revise code or design`. Architecture is not finished before code begins, and code is not high quality when it implements a philosophy the real slice disproves.

## 1. Read before writing

Use the environment's available tools; their names do not matter.

Read in order:

1. repository/domain instructions;
2. target file in full;
3. callers, callees, public types, tests, configuration, and persistence involved;
4. one or two adjacent implementations;
5. relevant build/test/release commands.

An adjacent implementation is evidence of a pattern, not permission to erase target-specific behavior.

For ambiguous or high-risk work, state:

```text
Behavior: observable result to change
Owner: layer/object that should own it
Scope: allowed files/modules
Do not change: contracts and behavior to preserve
Flow: input → state → side effect → output
Invariants: success, error, cancellation, retry
Unknowns: assumptions requiring evidence
```

If the flow cannot be stated, continue reading.

## 2. Find the owner before the implementation

Ask:

1. Is this a current verified need?
2. Does the repository already own the helper, data, or rule?
3. Can the standard library or platform express it transparently?
4. Would a mature dependency own required hard semantics without obscuring needed control, observability, or defining behavior?
5. Is this a reusable mechanism or one workflow/deployment policy?
6. What measurement or second real use case would justify more machinery?

Typical ownership:

- wire translation → protocol adapter;
- cross-provider retry/recovery → session/orchestration;
- visual presentation → UI;
- domain result calculation → one upstream owner, never recomputed by UI;
- deployment-specific polling/queues → external process when CLI/RPC already exists;
- retry, backoff, poison-task handling, and restart → the queue/supervisor contract unless explicitly assigned to the wrapper;
- temporary display choice → local state, not permanent settings;
- missing continuation/reset semantic → one explicit primitive, not replayed old input.

When simplifying, porting, or reimplementing a system, preserve its observable contracts, owner boundaries, and correctness floor; omit unrelated mechanisms. Do not copy its package graph or erase behavior the current task requires.

Do not add a factory, one-implementation interface, registry, manager, strategy hierarchy, event framework, setting, retry system, cache, or plugin point for hypothetical growth.

## 3. Use the direct code shape

Default to:

```text
plain object/record/struct + tagged union
array/list + set + map
for + while + if + exhaustive switch/match
one function following one complete data flow
small pure helpers after logic stabilizes
```

Rules:

- Divide functions by responsibility and data-flow direction, not a line limit.
- Keep a cohesive protocol loop together when splitting would scatter ordering and partial state.
- Use exhaustive static dispatch for a small fixed set; use a registry only for actual runtime registration.
- Use early return/continue to keep the main path flat.
- Name concrete actions and domain values; avoid vague Manager/Processor/Handler names.
- Keep messages/config/events serializable when identity and methods add no value.
- Consume structured upstream results instead of recomputing them downstream.
- Derive one mode from another when semantics are identical; do not maintain parallel implementations.
- Prefer two clear passes to one clever reducer when they express independent rules.
- Explain external quirks and reasons in comments; do not narrate syntax.
- Let realistic measurements override a standard-library or zero-dependency preference.

A second real implementation is evidence for abstraction; “maybe later” is not. Externalization is recursive: a thin wrapper must not quietly recreate retry, scheduling, persistence, or observability policies that were rejected from the core. Default to fail-fast and let the established queue/supervisor own recovery unless requirements say otherwise.

## 4. Keep one state owner

Do not represent the same mutable fact twice. If each view owns `expanded`, the parent sends `toggle`; it does not also maintain a second `expanded` flag unless synchronization semantics require it.

For async state, streams, queues, sessions, tools, terminals, and destructive I/O, preserve this floor:

- single-flight, explicit queueing, or independent per-run state;
- `validate → reduce state → publish event`;
- observer failure cannot terminate the producer;
- every lifecycle, iterator, and promise settles exactly once;
- cancellation prevents new side effects;
- queue wakeup and termination have no final-check race;
- network/model/plugin/persisted values receive runtime validation;
- partial, truncated, stale, or otherwise incomplete upstream results cannot authorize downstream side effects unless the contract explicitly permits it;
- destructive replacement is atomic where data loss matters;
- terminal/resources restore on success, error, signal, and cancellation;
- bytes/code units, graphemes, and display cells are not conflated.

Use a small state object and switch when sufficient. Do not add a framework to satisfy these invariants, and do not omit the invariants to keep code short.

## 5. Make the smallest complete change

- Change the fewest owners necessary.
- For a bug, trace callers and sibling paths; fix the earliest shared broken invariant.
- Preserve unrequested keyboard behavior, layout, API, serialization, and failure semantics.
- Avoid opportunistic renames, formatting, prose changes, and adjacent cleanup.
- Delete superseded code and imports instead of retaining speculative fallbacks.
- Do not hand-edit generated output when a generator owns it.
- Do not add scaffolding “for later.”

If implementation reveals the proposed owner is wrong, stop and restate the flow.

## 6. Validate with evidence

Use the repository's native commands and keep complete output.

At minimum:

1. add one deterministic check for non-trivial branches, parsers, state transitions, safety/money paths, or destructive operations;
2. run tests for the changed owner;
3. run required type/build/lint checks;
4. use a clean build for package/release work;
5. test realistic terminal, filesystem, timing, stream, and platform claims; before calling a workflow usable, cross one faithful outer boundary relevant to its deployment because seam tests do not verify invocation, wiring, framing, or packaging;
6. inspect the final diff for unrelated behavior, dependencies, generated files, docs, and contracts.

Skipped live tests, mock call counts, truncated logs, and “did not throw” are not complete evidence.

## 7. Review and report

Challenge the result:

- Can a mechanism, configuration path, duplicate computation, or fallback be deleted?
- Is the remaining code in the correct owner?
- Did simplicity remove a lifecycle or safety invariant?
- Did the change preserve target-specific behavior?
- What evidence would reverse this design?

Report only verified facts:

```text
Changed: observable behavior and files
Reused/deleted: mechanisms avoided or removed
Verified: exact checks and environments
Not verified: keys, platforms, scale, release, or integration gaps
Remaining risk: known boundary or ceiling
```

Do not claim “perfect,” “everything works,” or “production-ready” after partial checks.

## Boundary

Learn Pi's directness, not its early defects. Never preserve a race, hanging stream, fail-open validator, unsafe dynamic evaluation, Unicode corruption, unverified executable download, or non-atomic destructive write because it appeared in the source that inspired this skill.
