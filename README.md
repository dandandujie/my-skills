# my-skills

Claude Code Skills 集合仓库 — 模块化扩展包，为 Claude 提供专业领域知识和工作流。

## Skills 列表

| Skill | 简介 |
|-------|------|
| [agent-browser](agent-browser/) | 浏览器自动化。三层架构：`web_scan` 读取页面、`web_execute_js` 执行 JS/CDP 命令、`ljqCtrl` 物理鼠标键盘模拟。操作用户真实浏览器，保留登录态和 Cookie。参考https://github.com/lsdefine/GenericAgent项目 |
| [github-helper](github-helper/) | 本地 GitHub 仓库管理。自动扫描、克隆、同步仓库，维护可检索知识库，支持 Issue/PR 查询。通过 `gh` CLI 和 GitHub MCP 集成。 |
| [karpathy-style](karpathy-style/) | Karpathy-style 极简开发工作流。强调可度量目标、热路径成本模型、Taste Acquisition Loop、Negative-Space Gate、实验账本和复杂度审查，帮助 AI 写出更小、更可验证、更少抽象的代码。 |
| [llm-wiki](llm-wiki/) | Karpathy LLM Wiki 风格的项目知识库工作流。把 `AGENTS.md` / `CLAUDE.md` 作为路由，把 `.llm-wiki/` 作为可演化的项目上下文、结构索引和生命周期管理层。 |

## 全局提示词

- [KARPATHY_AGENT_PROMPT.md](KARPATHY_AGENT_PROMPT.md) 可复制到 `AGENTS.md` / `CLAUDE.md`，作为 Karpathy-style 开发模式的全局约束。

---

## 友情链接

- [linux.do](https://linux.do)
