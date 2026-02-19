# Claude Workflow Kit

一套运行在 Claude Code 之上的工作流系统。通过 CLAUDE.md 指令层、Skills 能力层、Hooks 自动化层三层协作，实现阶段驱动的任务管理和持续学习。

## 架构总览

```
┌─────────────────────────────────────────────────────┐
│                    CLAUDE.md                         │
│         行为指令 · 阶段路由表 · 反合理化规则           │
│         （Claude 每次会话启动时自动加载）               │
└──────────────────────┬──────────────────────────────┘
                       │ 指导
┌──────────────────────▼──────────────────────────────┐
│                    Skills 层                         │
│  discovery · planning · execution · diagnosis · ...  │
│         （Claude 通过 Skill 工具按需加载）              │
└──────────────────────┬──────────────────────────────┘
                       │ 触发 / 被观察
┌──────────────────────▼──────────────────────────────┐
│                    Hooks 层                          │
│  session-start · observe · phase-manager · ...       │
│         （Claude Code 在生命周期事件时自动执行）         │
└──────────────────────┬──────────────────────────────┘
                       │ 写入 / 读取
┌──────────────────────▼──────────────────────────────┐
│                 Homunculus 持久层                     │
│     observations.jsonl · instincts/ · sessions/      │
│         （跨会话持久化的学习数据）                      │
└─────────────────────────────────────────────────────┘
```

## 一次会话的完整生命周期

### 1. 会话启动

```
Claude Code 启动
    │
    ├─→ 自动加载 CLAUDE.md（阶段路由表、行为规范）
    │
    └─→ 触发 SessionStart 事件
            │
            └─→ session-start.js
                  ├─ 扫描 sessions/ 找最近 7 天的会话文件
                  ├─ 读取 projects/<项目>/phase-state.json
                  ├─ 如果有未完成的阶段，输出提醒：
                  │    "[系统] 当前阶段：planning"
                  │    "[系统] 请执行：Skill(skill: "planning")"
                  └─ 检测包管理器（npm/yarn/pnpm）
```

### 2. 用户发出请求

```
用户输入
    │
    └─→ Claude 根据 CLAUDE.md 中的阶段路由表判断：
          │
          ├─ 现实与预期有偏差？        → Skill("diagnosis")
          ├─ 在谈系统/Skill 本身？     → Skill("self-evolve")
          ├─ 不确定用户真正想要什么？    → Skill("discovery")
          ├─ 目标清楚但不知道怎么做？    → Skill("planning")
          └─ 目标和路径都清楚？         → Skill("execution")
```

### 3. 工作过程中

每次 Claude 调用工具（Edit/Write/Bash/Read/Grep/Glob），都会触发两条 Hook 链：

```
Claude 调用工具（如 Edit）
    │
    ├─→ PreToolUse 事件（Edit|Write 时触发）
    │       └─→ suggest-compact.js
    │             └─ 计数器 +1，达到 50 次时提醒考虑 /compact
    │
    ├─→ [工具实际执行]
    │
    └─→ PostToolUse 事件
            ├─→ observe.js（matcher: Edit|Write|Bash|Read|Grep|Glob）
            │     └─ 将工具名、输入、输出写入 homunculus/observations.jsonl
            │
            └─→ phase-manager.js（matcher: AskUserQuestion）
                  └─ 检测用户回答中是否包含阶段转换关键词
                     如 "进入 Planning" → 写入 phase-state.json
                     → 输出 "[系统] 阶段已切换到 planning"
```

### 4. 阶段转换

```
Claude 通过 AskUserQuestion 询问用户是否切换阶段
    │
    └─→ 用户选择 "进入 Planning"
          │
          ├─→ phase-manager.js 捕获到关键词
          │     └─ 更新 projects/<项目>/phase-state.json
          │          { "current_phase": "planning", "last_transition": "..." }
          │
          └─→ Claude 加载对应 Skill
                └─ Skill("planning") → 展开 skills/planning/SKILL.md 的完整指令
```

阶段流转图：

```
discovery → planning → execution → documentation-update → deploy
     ↑           ↑          ↓              ↓                  ↓
     └───────────┴──────── diagnosis ←─────┴──────────────────┘
```

### 5. 上下文压缩

```
Claude 即将执行 /compact
    │
    └─→ PreCompact 事件
          └─→ pre-compact.js
                ├─ 在 sessions/compaction-log.txt 记录压缩时间
                └─ 在当前会话文件中插入压缩标记
```

### 6. 会话结束

```
Claude 会话结束
    │
    ├─→ Stop 事件
    │     └─→ check-console-log.js
    │           └─ 扫描 git diff 中的 .js/.ts 文件
    │              如果发现 console.log → 输出警告
    │
    └─→ SessionEnd 事件
          ├─→ session-end.js
          │     └─ 创建/更新 sessions/YYYY-MM-DD-<id>-session.tmp
          │        记录会话时间、完成项、进行中项
          │
          └─→ evaluate-session.js（学习系统入口）
                ├─ 读取 observations.jsonl 中本次会话的记录
                ├─ 如果观察数 < 5 或会话消息数 < 5 → 跳过
                └─ 满足条件 → 启动学习流程（见下节）
```

## 学习系统（Homunculus）

从观察到直觉的完整链路：

```
observe.js                     evaluate-session.js              run-observer.js
 (每次工具调用)                   (会话结束时)                      (后台进程)
     │                               │                               │
     │ 追加写入                       │ 过滤本会话记录                  │
     ▼                               ▼                               ▼
observations.jsonl ──────→ 嵌入 observer-prompt.md ──────→ claude --model haiku
                                                                     │
                                                              解析 ===INSTINCT=== 块
                                                                     │
                                                                     ▼
                                                          instincts/personal/<id>.md
                                                          (YAML frontmatter + Markdown)
                                                          ┌─────────────────────┐
                                                          │ id: xxx             │
                                                          │ trigger: "..."      │
                                                          │ confidence: 0.3-0.85│
                                                          │ domain: workflow    │
                                                          │ # Title            │
                                                          │ ## Action           │
                                                          │ ## Evidence         │
                                                          └─────────────────────┘
```

直觉的生命周期：
- 首次检测到模式 → confidence 0.3
- 被用户确认 → +0.05
- 与用户行为矛盾 → -0.1
- 每周自然衰减 → -0.02
- 达到 0.7+ → 可通过 `/evolve` 聚类为 Skill/Command/Agent

## 组件依赖关系

```
scripts/hooks/*.js
    └─→ 依赖 scripts/lib/
          ├── utils.js          # 文件操作、路径、日期工具函数
          ├── session-manager.js # 会话文件管理
          ├── session-aliases.js # 会话别名
          └── package-manager.js # 包管理器检测

skills/continuous-learning-v2/
    ├── SKILL.md                # /learn /instinct-status /evolve 命令定义
    ├── config.json             # 观察/直觉/演进的参数配置
    ├── agents/observer.md      # 观察器 agent 定义
    └── scripts/instinct-cli.py # 直觉管理 CLI

homunculus/
    ├── observer-prompt.md      # LLM 提炼用的 prompt 模板
    ├── observations.jsonl      # observe.js 写入，evaluate-session.js 读取
    ├── instincts/personal/     # run-observer.js 写入，self-evolve Skill 读取
    ├── instincts/inherited/    # 手动导入的外部直觉
    └── evolved/                # /evolve 产出的高级结构
```

## Skills 清单

### 阶段管理（核心）

| Skill | 调用时机 | 职责 |
|-------|----------|------|
| discovery | 新需求/新想法/不确定 | 通过提问拆解，输出结构化理解 |
| planning | 目标清楚，路径不清楚 | 设计可行的执行方案 |
| execution | 目标和路径都清楚 | 通过 Subagent 高效执行 |
| diagnosis | 出现问题/错误/偏差 | 找到根因并解决 |
| self-evolve | 查看/应用学习积累 | 将成熟直觉演进为 Skill |
| documentation-update | 功能完成后 | 确保文档与代码一致 |
| deploy | 部署上线 | 部署与环境同步 |

### 功能增强

| Skill | 职责 |
|-------|------|
| continuous-learning-v2 | 直觉学习系统的管理界面（/learn /evolve） |
| smart-fetch | 反爬站点的智能抓取（curl_cffi → DrissionPage → Jina 三级降级） |
| key-reader | 安全读取外部 API 密钥 |
| recall | 从历史会话中召回相关记忆 |
| agent-browser | 浏览器自动化 CLI |

## 环境配置：glo.env

`glo.env` 是整个系统的密钥和基础设施配置中心，不入库（含敏感信息）。`key-reader` Skill 从此文件读取密钥，多个 Skill 和 MCP 服务器依赖其中的配置。

需要在 `~/.claude/glo.env` 中配置以下内容：

```env
# LLM API（smart-fetch、recall 等 Skill 可能调用）
DEEPSEEK_API_KEY=
DEEPSEEK_BASE_URL=https://api.deepseek.com
SILICONFLOW_API_KEY=
SILICONFLOW_BASE_URL=https://api.siliconflow.cn/v1
AIPING_API_KEY=
AIPING_BASE_URL=https://aiping.cn/api/v1

# 容器镜像仓库
GHCR_PAT=

# 开发服务器
IP=
USER_NAME=
PASSWORD=

# 火山引擎（Seedream MCP 生图）
ARK_API_KEY=
```

## 安装

```bash
git clone <repo-url> ~/.claude
node ~/.claude/setup.js        # 注入 hooks 配置到 settings.json
# 然后创建 glo.env 并填入你的密钥
```
