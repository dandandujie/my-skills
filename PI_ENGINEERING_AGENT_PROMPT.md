# Engineering policy

Apply these rules to every design, implementation, bug fix, refactor, and code review in this repository. They are language-, tool-, and agent-independent.

## Objective

Minimize independent mechanisms, state combinations, and error owners—not raw line count.

Prefer direct code only after understanding the real data flow. A short patch in the wrong layer is worse than a larger change that restores one clear owner. Historical examples inform ownership and trade-offs; current requirements determine concrete keys, labels, limits, and interaction semantics.

## Project-to-code loop

For a new project or broad feature, establish before choosing modules:

```text
User/Friction: who is blocked doing what?
Gestalt: properties the experience must preserve
Non-goals: users, quality levels, and mechanisms not owned
Constraints: platform, privacy, cost, compatibility, safety
Core loop: input → canonical state → side effect → output
Owner map: canonical, transient, translation, policy, UI, recovery
Slice: first real end-to-end scenario
Evidence/Reversal: assumptions and facts that would change the design
```

Every important architecture decision should trace `constraint → owner/mechanism → rejected alternative → observable consequence`. Implement the thinnest real vertical slice before horizontal infrastructure. Let implementation feed back: duplicate state, opaque side effects, cross-layer plumbing, scattered lifecycle handling, or untestable claims are evidence to revise the owner, non-goal, or project thesis—not reasons to add another abstraction.

## Before editing

Read:

1. Repository/domain instructions.
2. The target file in full.
3. Callers, callees, public types, tests, configuration, and persistence involved.
4. One or two adjacent implementations.
5. Relevant build, test, and release commands.

Do not use an adjacent file as permission to erase target-specific behavior.

Establish:

```text
Behavior: observable result to change
Owner: layer/object that should own it
Scope: allowed files/modules
Do not change: contracts and behavior to preserve
Flow: input → state → side effect → output
Invariants: success, error, cancellation, retry
Unknowns: assumptions requiring inspection or experiment
```

If the flow is unclear, continue reading before writing.

## Decide whether code should exist

Ask in order:

1. Is this a current verified need?
2. Does the repository already contain the helper/data/pattern?
3. Does the language standard library solve it?
4. Can files, processes, CLI, version control, database constraints, or another platform primitive own it transparently?
5. Would a mature dependency own required hard semantics without obscuring needed control, observability, or defining behavior?
6. Is this a reusable mechanism or one workflow policy?
7. What measurement or second use case would justify a larger design?

When simplifying, porting, or reimplementing a system, preserve its observable contracts, owner boundaries, and correctness floor; omit unrelated mechanisms. Do not copy its package graph or erase behavior the current task requires.

Do not add a factory, one-implementation interface, registry, manager, strategy hierarchy, event framework, configuration option, retry system, cache, or plugin point for hypothetical growth.

## Default code shape

Prefer:

```text
plain object/record/struct
+ tagged/discriminated union
+ array/list, set, map
+ for, while, if, exhaustive switch/match
+ one function following one complete data flow
+ small pure helpers after logic stabilizes
```

Rules:

- Divide functions by responsibility and data-flow direction, not arbitrary line count.
- Keep a cohesive protocol loop together when splitting would scatter shared state and ordering.
- Use exhaustive static dispatch for a small fixed set; use a registry only for real runtime registration.
- Use early return/continue to keep the main path flat.
- Name concrete actions and domain values; avoid vague Manager/Processor/Handler names.
- Keep domain data serializable when identity and methods add no value.
- Consume upstream structured results; do not recompute them in presentation layers.
- Derive one mode from another when semantics are identical; do not maintain parallel implementations.
- Two clear passes are preferable to one clever reducer when they express independent rules.
- Comments explain external quirks, invariants, and reasons—not syntax.
- Reuse mature libraries or external tools for complex semantics; real measurements may override standard-library preference.

## Ownership and architecture

- Put protocol translation in adapters.
- Put cross-provider/workflow recovery in session/orchestration.
- Put presentation decisions in UI, not libraries.
- Keep deployment-specific polling/queues/integration outside a general core when a CLI/RPC/process boundary already exists.
- Externalization is recursive: a wrapper must not silently take ownership of retry, backoff, poison-task handling, persistence, or supervision unless the deployment contract assigns it there. Default to fail-fast and let the established queue/supervisor own recovery.
- Treat prompt macros as text expansion, not plugins or subagents.
- Treat transient interaction as local state, not permanent configuration.
- If a workaround saves and replays old input, check whether one small missing primitive should be added instead.

## Correctness floor

Simple code must still guarantee:

- one mutable owner;
- single-flight, explicit queueing, or independent per-run state;
- runtime validation before trusting network/model/plugin/persisted values;
- partial, truncated, stale, or otherwise incomplete upstream results cannot authorize downstream side effects unless the contract explicitly permits it;
- state reduction before event publication;
- observer failures isolated from producers;
- every lifecycle, iterator, and promise reaches one terminal state;
- cancellation prevents new side effects;
- queue wakeup and termination have no final-check race;
- destructive writes are atomic where data loss matters;
- terminal/resources restore on success, error, signal, and cancellation;
- Unicode storage offsets, graphemes, and display cells are not conflated.

Do not introduce a state-machine framework if a state object and switch can express these invariants. Do not omit the invariants to keep code short.

## Scope discipline

- Change the fewest owners necessary.
- Do not opportunistically rename, reformat, rewrite text, or clean adjacent code.
- Preserve keyboard behavior, layout, API, serialization, and failure semantics not named by the task.
- Delete superseded code/imports rather than retaining speculative fallbacks.
- Do not hand-edit generated output when a generator owns it.
- Do not add scaffolding “for later.”

For a bug, trace every caller and sibling path, then fix the earliest shared broken invariant.

## Validation

Use the repository's own commands and keep complete output.

At minimum:

1. Add one deterministic check for non-trivial branches, parsers, state transitions, security/money paths, or destructive operations.
2. Run tests for the changed owner.
3. Run required type/build/lint checks.
4. Use a clean build for package/release work.
5. Test realistic terminal, filesystem, timing, stream, and platform claims. Before calling a workflow usable, cross one faithful outer boundary relevant to its deployment; seam tests do not verify invocation, wiring, framing, or packaging.
6. Inspect the final diff for unrelated behavior, dependencies, generated files, docs, and contracts.

Live tests, skipped tests, mock call counts, truncated logs, and “did not throw” checks do not replace deterministic boundary tests.

## Review questions

- Is a class or interface serving only one implementation?
- Is a static registry better expressed as an exhaustive switch?
- Is a helper called once and hiding the main flow?
- Is a configuration value actually transient UI state?
- Is a fallback swallowing a stable error?
- Is a result computed twice in different layers?
- Does mutable state have more than one owner?
- Does `as`/casting cross a runtime trust boundary?
- Can cancellation still start another side effect?
- Can EOF leave a result unresolved?
- Did the change alter unrequested behavior?
- What fact or measurement would reverse this design?

## Completion report

Report only verified facts:

```text
Changed: observable behavior and files
Reused/deleted: mechanisms avoided or removed
Verified: exact checks and environments
Not verified: keys, platforms, scale, release, or integration gaps
Remaining risk: known boundary or ceiling
```

Do not claim “perfect,” “everything works,” or “production-ready” after partial checks.
