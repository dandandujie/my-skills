---
name: llm-wiki
description: "Create or retrofit AGENTS.md and CLAUDE.md into an LLM Wiki router/index for project-level or global AI-agent memory. Use when asked for a Karpathy-style LLM Wiki, Markdown knowledge-base lifecycle management, token-saving codebase context index, self-updating agent instructions, or converting AGENTS/CLAUDE into a persistent .llm-wiki."
---

# LLM Wiki

## Core Model

Turn `AGENTS.md` and/or `CLAUDE.md` into a thin router. Keep stable facts, codebase maps, decisions, workflows, and open questions in `.llm-wiki/`.

North Star Metric: the next agent should recover the correct project context by opening the router plus the smallest relevant set of wiki pages, with no duplicated stale facts in router files.

Use three layers:

1. Router: `AGENTS.md` and/or `CLAUDE.md`; rules, load order, route table, lifecycle obligations.
2. Wiki: `.llm-wiki/*.md`; compiled project/global knowledge that agents update.
3. Sources: code, tests, docs, issue threads, chats, raw notes; treated as evidence, not copied blindly.

## Workflow

1. Determine scope.
   - Project scope: use the repository root and create/update repo-local `AGENTS.md`, `CLAUDE.md`, and `.llm-wiki/`.
   - Global scope: use the user's actual global instruction directory for the target agent tool; confirm the path before editing if it is outside the workspace.
   - If the user does not specify one router file, support both `AGENTS.md` and `CLAUDE.md`.

2. Classify the target before writing.
   - New/empty project: if the target has no meaningful project files yet, initialize the wiki skeleton and router files first, then leave content placeholders and first-audit questions.
   - Existing project: if the target contains source code, docs, config, tests, or existing `AGENTS.md`/`CLAUDE.md`, audit the project before creating final wiki content.
   - Treat `.git/`, dependency folders, generated build output, caches, binaries, and `.llm-wiki/` itself as non-source unless the user says otherwise.

3. Audit existing projects before scaffolding content.
   - Read existing `AGENTS.md` and `CLAUDE.md` in full. Their original project rules stay authoritative and must remain before the LLM Wiki block.
   - Systematically inspect the project structure, core source directories, README, architecture docs, package/build config, tests, API/schema files, and obvious entry points.
   - Extract project structure, functional design, module boundaries, workflows, commands, dependencies, terminology, risks, and open questions from evidence.
   - Do not invent project facts. Mark unknowns in `.llm-wiki/open-questions.md`.
   - Do not delete, move, or summarize away existing router-file rules unless the user explicitly asks for a rewrite.

4. Bootstrap the structure.
   - Prefer the deterministic helper for a first pass:

```bash
python3 /path/to/llm-wiki/scripts/bootstrap_llm_wiki.py /path/to/project
```

   - Use `--router-file` repeatedly to target specific router files.
   - Use `--scope global` for a global wiki, after confirming the target path.
   - Use `--dry-run` before editing sensitive global files.
   - For existing projects, run the helper only after the audit. Then replace placeholder wiki page content with evidence-backed project content.

5. Fill the wiki from evidence.
   - Read `references/wiki-pages.md` when creating or updating page content.
   - Keep `.llm-wiki/index.md` as the canonical route table and status page.
   - Put code layout and ownership in `project-map.md`, recurring commands in `workflows.md`, architectural choices in `decisions.md`, vocabulary in `glossary.md`, active uncertainty in `open-questions.md`, and notable agent work in `task-log.md`.

6. Retrofit router files.
   - Read `references/router-block.md` before editing `AGENTS.md` or `CLAUDE.md`.
   - Add or replace only the block between `<!-- LLM-WIKI:START -->` and `<!-- LLM-WIKI:END -->`.
   - If no managed block exists, append the LLM Wiki block after all existing project rules. Do not insert it before or inside original instructions.
   - Keep route entries short: what to open, when to open it, and what not to duplicate.

7. Maintain lifecycle sync.
   - Before doing work, read the router and only the wiki pages relevant to the task.
   - During work, update wiki pages when code structure, API contracts, commands, dependencies, decisions, or known risks change.
   - After work, update `task-log.md` and `index.md` if new routes, stale routes, or unresolved questions appeared.
   - If a fact belongs in one canonical wiki page, link to it elsewhere instead of duplicating it.

## Update Rules

- Treat stale wiki content as a bug. Fix it in the same change that made it stale.
- Prefer deleting outdated claims over adding exceptions.
- Cite local evidence in wiki entries with file paths, command outputs, issue links, or source document names.
- Do not add broad fallback rules that hide missing knowledge. Record uncertainty explicitly.
- Keep router files compact. If the block grows past a screen, move detail into `.llm-wiki/index.md`.
- Do not update `.llm-wiki/raw/` unless the user asks to preserve source notes or transcripts.

## Resources

- `scripts/bootstrap_llm_wiki.py`: safe scaffold and managed-block updater.
- `references/router-block.md`: router block template and placement rules.
- `references/wiki-pages.md`: canonical wiki page schemas.
- `references/prompts.md`: copy-ready prompts for users who want to invoke this as a prompt instead of an installed Skill.
