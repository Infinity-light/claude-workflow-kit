# Claude Workflow Kit

基于 Claude Code 的个人工作流系统，包含阶段管理、Hook 自动化和直觉学习。

## 包含什么

```
skills/           # 阶段管理 + 功能 Skills
scripts/hooks/    # 9 个生命周期 Hook 脚本
scripts/lib/      # Hook 依赖的工具库
homunculus/       # 直觉学习系统（ECC 架构）
agents/           # Agent 定义
CLAUDE.md         # 全局行为指令
```

## 阶段管理

```
discovery → planning → execution → documentation-update → deploy
     ↑           ↑          ↓              ↓                  ↓
     └───────────┴──────── diagnosis ←─────┴──────────────────┘
```

| 阶段 | 触发场景 |
|------|----------|
| discovery | 新需求、新想法、不确定的问题 |
| planning | 目标清楚，不知道怎么实现 |
| execution | 目标和路径都清楚，动手 |
| diagnosis | 出了问题，找根因 |
| self-evolve | 查看/应用学习系统积累的直觉 |

## Hook 链

| 事件 | 脚本 | 作用 |
|------|------|------|
| SessionStart | session-start.js | 加载上次会话上下文 |
| PostToolUse | observe.js | 捕获工具调用供学习 |
| PostToolUse | phase-manager.js | 检测阶段转换 |
| PreToolUse | suggest-compact.js | 逻辑边界建议 compact |
| PreCompact | pre-compact.js | compact 前保存状态 |
| Stop | check-console-log.js | 检查遗留 console.log |
| SessionEnd | session-end.js | 会话结束持久化 |
| SessionEnd | evaluate-session.js | 提取可复用模式 |

## 安装

```bash
# 新用户：直接 clone
git clone <repo-url> ~/.claude

# 注入 hooks 到 settings.json
node ~/.claude/setup.js
# 然后编辑 ~/.claude/settings.json 填入你的 API token
```

```bash
# 已有 ~/.claude 的用户：拉取到已有目录
cd ~/.claude
git init
git remote add origin <repo-url>
git fetch
git merge origin/main --allow-unrelated-histories
node setup.js
```

## 日常使用

```bash
# 改了 Skill 或 Hook 后
cd ~/.claude && git add . && git commit -m "update: ..." && git push

# 换电脑
git clone <repo-url> ~/.claude && node ~/.claude/setup.js
```

## 不追踪的内容

- `settings.json` — 含 API token
- `sessions/` `cache/` `telemetry/` 等运行时数据
- 第三方 Skills（各自有独立仓库）
