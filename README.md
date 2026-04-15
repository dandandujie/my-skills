# my-skills

Claude Code Skills 集合仓库 — 模块化扩展包，为 Claude 提供专业领域知识和工作流。

## Skills 列表

| Skill | 简介 |
|-------|------|
| [agent-browser](agent-browser/) | 浏览器自动化。三层架构：`web_scan` 读取页面、`web_execute_js` 执行 JS/CDP 命令、`ljqCtrl` 物理鼠标键盘模拟。操作用户真实浏览器，保留登录态和 Cookie。 |参考https://github.com/lsdefine/GenericAgent项目
| [github-helper](github-helper/) | 本地 GitHub 仓库管理。自动扫描、克隆、同步仓库，维护可检索知识库，支持 Issue/PR 查询。通过 `gh` CLI 和 GitHub MCP 集成。 |

---

## 友情链接

- [linux.do](https://linux.do)
