# Router Block

Use this reference when creating or retrofitting `AGENTS.md` or `CLAUDE.md`.

## Placement

- Preserve existing user instructions.
- If a managed block already exists, replace only the content between the markers.
- If no managed block exists, append the block after all existing project guidance.
- Never delete, reorder, or compress original project rules in `AGENTS.md` or `CLAUDE.md` unless the user explicitly requests a rewrite.
- Keep the block identical across `AGENTS.md` and `CLAUDE.md` unless the user explicitly wants tool-specific differences.

For existing repositories, place this block only after auditing the project structure, source code, docs, configs, tests, and existing router files. The router block should point to wiki pages already filled with evidence-backed project context, not just placeholders.

## Template

```markdown
<!-- LLM-WIKI:START -->
## LLM Wiki Router

This project uses `.llm-wiki/` as the persistent knowledge layer. This file is only the router and lifecycle contract.

### Load Order

1. Read this router block.
2. Open `.llm-wiki/index.md`.
3. Open only the route pages needed for the current task.
4. Verify important claims against source files before editing behavior.

### Routes

- `.llm-wiki/index.md`: route table, freshness status, current context budget.
- `.llm-wiki/project-map.md`: codebase layout, module ownership, boundaries, important entry points.
- `.llm-wiki/workflows.md`: setup, test, build, release, debugging, and repeated operational commands.
- `.llm-wiki/decisions.md`: architectural decisions, constraints, rejected alternatives, and rationale.
- `.llm-wiki/glossary.md`: project vocabulary, domain terms, acronyms, and naming conventions.
- `.llm-wiki/open-questions.md`: unknowns, stale assumptions, blocked investigations, and required confirmations.
- `.llm-wiki/task-log.md`: notable agent work, changed files, verification, and follow-up context.

### Lifecycle Rules

- Before work: load only the wiki pages relevant to the request.
- During work: update wiki pages when code structure, commands, contracts, dependencies, decisions, or risks change.
- After work: update `task-log.md`; update `index.md` if routes, freshness, or open questions changed.
- Do not duplicate long facts in this router. Link to the canonical wiki page.
- If wiki content conflicts with source code, source code wins; update the wiki immediately.
<!-- LLM-WIKI:END -->
```

## Global Variant

For global instructions, keep the same shape but make routes point to a global wiki directory chosen by the user, for example a dot-directory under their agent configuration home. Do not assume a global path when the tool ecosystem is unknown.

Use global pages for stable personal/team preferences, reusable debugging playbooks, naming conventions, and cross-project policies. Keep project-specific facts in the project wiki.
