# Direct code shapes

Load this reference when deciding how to express functions, types, protocols, UI, CLI, persistence, or extensions.

## Table of contents

1. Function boundaries
2. Types and state
3. Dispatch and protocols
4. UI and terminal
5. CLI, files, and processes
6. Persistence and branching
7. Extraction threshold

## 1. Function boundaries

A function is cohesive when it follows one complete data-flow direction, even if it is long.

Prefer:

```text
wire stream → normalized event stream
normalized message → provider request
input event → editor state transition
CLI args → runtime options
```

Do not split only to satisfy a line count. Extract when at least one is true:

- the logic is pure and independently testable;
- it has two real callers;
- it names a stable domain operation;
- extraction reduces shared mutable state;
- the main flow becomes easier to read.

Keep protocol events together when extraction would pass the same partial state through many handlers.

## 2. Types and state

Prefer serializable values and tagged unions:

```ts
type Message =
  | { role: "user"; content: UserContent }
  | { role: "assistant"; content: AssistantContent }
  | { role: "toolResult"; toolCallId: string; content: ResultContent };
```

Use classes only when identity, encapsulated invariants, or real behavior matters. Do not use class inheritance to model JSON payload variants.

Use the smallest data structure matching access:

- sequence/order: array/list;
- membership: set;
- lookup by stable ID/index: map;
- tiny single-owner state: ordinary record/object;
- append-only inspection: JSONL or equivalent log.

When upstream events interleave, use their ID/index. A single `currentItem` is valid only for a proven single channel.

## 3. Dispatch and protocols

Small fixed set:

```ts
switch (api) {
  case "a": return runA();
  case "b": return runB();
  default: return assertNever(api);
}
```

Runtime registration requirement:

```text
registry/plugin loader is justified
```

Do not confuse provider brand with wire protocol. Dispatch on the stable protocol axis; represent brand-specific capabilities as data only when actual behavior differs.

Keep separate adapters when protocol ordering and state differ. Extract shared pure operations, not a base class filled with hooks.

Use SDK event names directly in branches. Comments should record provider/version quirks.

## 4. UI and terminal

For a vertically composed text UI, start with:

```ts
render(width): string[]
```

- vertical layout: concatenate arrays;
- render batching: one pending boolean plus next tick;
- diff: first changed line, then redraw suffix;
- leaf cache: exact render inputs such as text + width;
- fixed token types: switch;
- Markdown syntax: mature parser, local terminal renderer;
- width/grapheme rules: mature library/platform data.

Upgrade only after requirements appear for overlapping nodes, horizontal constraints, mouse hit testing, variable-height virtualization, or many independent animations.

Terminal simplification may not remove:

- trusted ANSI vs untrusted text separation;
- incremental input framing;
- raw mode/cursor/paste restoration;
- grapheme and cell-width correctness;
- deterministic virtual-terminal tests.

## 5. CLI, files, and processes

Small CLI without subcommands can use one argument loop. Validate unknown flags, missing values, invalid enums, and dependent options.

Use the filesystem hierarchy as context hierarchy when that is the product rule; do not invent a workspace graph.

Use external processes for deployment-specific orchestration when a stable CLI/RPC boundary exists:

```text
queue → wrapper process → tool CLI/RPC → result
```

Use mature search tools instead of reimplementing ignore semantics and indexing when real repository-scale measurements justify them.

Exact edit is safer than a guessed fuzzy edit:

```text
require one exact occurrence → replace → otherwise return ambiguity
```

Use atomic replacement for destructive writes where concurrent changes or partial files matter.

## 6. Persistence and branching

Append-only JSONL is useful when sessions are small, inspectable, and scriptable. Include:

- schema version;
- stable session ID;
- runtime/model/tool metadata needed for replay;
- explicit warnings for malformed entries.

Parse once, then project state. Do not repeatedly scan the same file for each property.

A branch can copy a message prefix if lineage queries are not required. If the product promises a tree, record parent ID and branch point rather than pretending copied files form a graph.

A Markdown slash command can remain a prompt macro. Do not call it a plugin or subagent runtime unless it can actually register behavior, tools, lifecycle, or state.

## 7. Extraction threshold

Use this sequence:

```text
first occurrence  → direct local code
second occurrence → compare semantics; perhaps one function
stable variants   → parameter/data table
runtime consumers → interface/registry only if required
```

Never jump directly from first occurrence to framework.
