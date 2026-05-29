# Prompts

Use these prompts when the user wants a copy-ready instruction instead of installing the Skill.

## Create Project LLM Wiki

```text
Use $llm-wiki. In this repository, create or retrofit AGENTS.md and CLAUDE.md as thin LLM Wiki routers. If this is a new or empty project, initialize the wiki skeleton. If the repo already has code, docs, config, tests, or existing AGENTS.md/CLAUDE.md, first audit the project structure, functional design, core source files, workflows, and existing instructions; then create .llm-wiki/ with evidence-backed pages. Preserve existing router-file rules and append the LLM-WIKI block after them. Keep router files compact and make future agents update the wiki whenever project structure, commands, contracts, dependencies, decisions, or known risks change.
```

## Retrofit Existing Router Files

```text
Use $llm-wiki. This project already has AGENTS.md and/or CLAUDE.md. Read those files in full, audit the repo's structure, source code, docs, configs, tests, workflows, and functional design, then add an LLM-WIKI managed block after the existing instructions. Preserve the original project rules exactly unless I explicitly ask for a rewrite. Put durable project context in .llm-wiki/ pages and flag uncertain or conflicting facts in .llm-wiki/open-questions.md.
```

## Create Global LLM Wiki

```text
Use $llm-wiki. Create a global LLM Wiki for my agent instructions. First confirm the global instruction path to edit. Then create or retrofit AGENTS.md and CLAUDE.md as routers to a global wiki directory. Keep global pages limited to stable preferences, cross-project workflows, naming conventions, and reusable debugging playbooks. Do not put project-specific facts in the global wiki.
```

## Maintain After A Change

```text
Use $llm-wiki. After completing this code change, update the LLM Wiki if any code structure, command, dependency, API contract, architectural decision, workflow, or known risk changed. Keep AGENTS.md and CLAUDE.md as routers only; update .llm-wiki/ pages for durable facts and record the verification in .llm-wiki/task-log.md.
```
