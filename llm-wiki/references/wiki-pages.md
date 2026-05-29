# Wiki Pages

Use these schemas when creating or updating `.llm-wiki/`. Keep pages short, linked, and evidence-backed.

## Shared Header

Every page should begin with:

```markdown
# Page Title

- scope: project | global
- last_reviewed: YYYY-MM-DD
- source_of_truth: short description of where facts are verified
- update_trigger: when an agent must update this page
```

## `.llm-wiki/index.md`

Purpose: canonical navigation and freshness status.

Sections:

```markdown
## Context Budget

- default_load: router + this file
- task_load_rule: open the smallest route set that can answer the current request

## Route Table

| Need | Open | Notes |
| --- | --- | --- |
| Code layout | `project-map.md` | Entry points, boundaries, ownership |

## Freshness

| Page | Last reviewed | Risk | Next review trigger |
| --- | --- | --- | --- |

## Current Invariants

- Invariant that should remain true across the project.

## Open Questions Snapshot

- Link to `open-questions.md` entries that affect current work.
```

## `.llm-wiki/project-map.md`

Purpose: compiled codebase map.

Include:

- Directory map with short intent, not a full file tree.
- Main entry points and data/control flow.
- Module boundaries and ownership rules.
- Generated files and files agents should avoid editing manually.
- Pointers to source files for claims.

Update when directories, entry points, module boundaries, public APIs, or generated artifacts change.

## `.llm-wiki/workflows.md`

Purpose: repeated commands and operational procedures.

Include:

- Install/setup commands.
- Test, lint, typecheck, build, and run commands.
- Environment assumptions and required services.
- Known failure modes with direct diagnostic commands.

Update when scripts, package managers, CI behavior, env vars, ports, or service dependencies change.

## `.llm-wiki/decisions.md`

Purpose: architectural memory.

Decision entry format:

```markdown
## YYYY-MM-DD - Decision Title

- status: proposed | accepted | superseded
- context:
- decision:
- rationale:
- rejected_alternatives:
- consequences:
- evidence:
```

Update when a durable technical choice is made, reversed, or constrained by new evidence.

## `.llm-wiki/glossary.md`

Purpose: project vocabulary and naming.

Include domain terms, acronyms, external service names, internal aliases, and "do not confuse X with Y" notes. Keep definitions short and link to evidence.

## `.llm-wiki/open-questions.md`

Purpose: make uncertainty visible.

Entry format:

```markdown
## Question

- status: open | blocked | answered
- why_it_matters:
- evidence_checked:
- owner_or_next_step:
- answer:
```

Never hide missing knowledge with a default assumption. If a question blocks safe work, ask the user.

## `.llm-wiki/task-log.md`

Purpose: durable work trail for future agents.

Entry format:

```markdown
## YYYY-MM-DD - Short Task Name

- request:
- changed:
- verified:
- wiki_updates:
- residual_risk:
```

Log only entries that will help a future agent understand project state. Do not turn this into a chat transcript.

## `.llm-wiki/raw/`

Purpose: optional provenance store for source notes, pasted transcripts, meeting notes, or imported documents.

Do not load raw files by default. Promote durable facts into the compiled wiki pages and cite the raw source filename.
