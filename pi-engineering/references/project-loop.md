# Project philosophy ↔ code feedback

Load for a new project, broad product decision, or unclear governing idea. Use it together with the main implementation discipline, not as a separate architecture phase.

## Derive the project, do not summarize the wishlist

Establish:

```text
User/Friction: who is blocked doing what?
Gestalt: properties the experience must preserve
Non-goals: users, quality levels, and mechanisms not owned
Constraints: platform, privacy, cost, compatibility, safety
Core loop: input → canonical state → side effect → observable output
Owners: canonical, transient, translation, policy, UI, recovery
Slice: first real end-to-end scenario
Evidence/Reversal: assumptions and facts that would change the design
```

“Simple,” “fast,” and “extensible” are not a philosophy. A principle matters only when it rejects an alternative, assigns responsibility, or changes an observable experience. For an existing project, recover this logic from behavior, history, code, and rejected changes; do not replace it with generic best practices.

Recommend the strongest interpretation. Ask only when missing product semantics would make an irreversible choice arbitrary.

## Translate gestalt into ownership

Record important choices as:

```text
constraint → owner/mechanism → rejected alternative → observable consequence
```

Correctness-critical state belongs where it remains inspectable and recoverable. Platform/provider state may be treated as a cache only when loss can be reconstructed from canonical state. Prefer existing repository structures, files, processes, CLI, platform primitives, standard libraries, and mature dependencies before inventing another mechanism.

Architecture is an ownership map around one core loop, not a list of nouns. Do not build plugin systems, generic repositories, event buses, workflow graphs, configuration matrices, dashboards, or multi-agent infrastructure before a real vertical slice requires them.

When simplifying, porting, or reimplementing a system, preserve observable contracts, owners, and the correctness floor while omitting unrelated mechanisms. Use a mature dependency when it owns needed hard semantics; reject it when it obscures required control or observability. A second real demand or hard edge can reverse a narrow local mechanism.

## Let the vertical slice test both layers

Build one representative path:

```text
real input
→ validate
→ canonical state transition
→ one real or faithful side effect
→ observable output
→ persisted/replayable evidence when required
```

Before coding, state what this slice tests about the architecture. After coding, inspect the evidence:

- duplicate mutable state questions the owner;
- values threaded across many layers question the boundary;
- hidden retries or side effects violate observability;
- UI reparsing domain output reveals duplicate ownership;
- untestable claims reveal a missing observable contract;
- a direct implementation that cannot preserve lifecycle semantics reveals a missing state transition;
- measured platform/tool failure can justify a dependency or narrow replacement;
- a green injected seam plus a broken real invocation reveals a missing faithful outer-boundary check.

Revise the owner, non-goal, slice, or project thesis when evidence disagrees. Do not preserve a mechanism merely because the design named it.

## Keep the philosophy falsifiable

Use the cheapest evidence capable of disproving the claim, then escalate:

```text
existing history / paper model
→ deterministic test
→ end-to-end slice
→ realistic platform or scale measurement
→ repeated use by the actual user
```

Preserve user value and observable contracts, not mechanism loyalty. A second real demand can justify extraction; predicted growth cannot. A proof of concept, personal tool, production service, safety boundary, and commercial product have different correctness ceilings—state which one is being built.

Final review must trace both directions:

```text
friction ↔ gestalt ↔ non-goals ↔ owners
    ↑                              ↓
real feedback ← checks ← direct vertical-slice code
```

A polished design document cannot compensate for code that creates different owners. Passing tests cannot compensate for a slice that violates the intended experience.