# Claude Workflow Kit

一套运行在 Claude Code 之上的 Skill-First 工作流系统。通过 CLAUDE.md 指令层和 Skills 能力层的双层协作，实现阶段驱动的任务管理。

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
└─────────────────────────────────────────────────────┘
```

## 核心原则：Skill-First

**Skill 是唯一的工作单元。整个工作流不是"流程里偶尔调用 Skill"，而是"一切工作都是 Skill 的编排"。**

### 四层 Skill-First 法则

**第一层：优先使用现有 Skill**
做任何事之前，先问一个问题：**有没有对应的 Skill？**
- 有 → 立即加载，按 Skill 指导执行
- 没有 → 进入第二层

**第二层：遇到困境，先找 Skill 市场**
当现有 Skill 无法覆盖当前任务时，**先用 find-skills 搜索市场上是否有可用的 Skill**，不要直接自己动手硬做。

**第三层：没有 Skill，找 GitHub 项目并考虑转化**
如果市场上也没有对应的 Skill，去搜索有没有成熟的 GitHub 项目能实现这个功能。找到后考虑用 `skill-creator` 将其转化为 Skill。

**第四层：任务完成后，反哺 Skill 体系**
每次任务完成后，主动思考：
- 现有 Skill 是否需要优化/迭代？→ 用 `skill-creator` 更新
- 这次积累的经验能否 Skill 化？→ 用 `skill-creator` 创建新 Skill

## 阶段路由

```
discovery → planning → execution → deploy → verification → documentation-update
                                     ↑          ↓          ↓
                                     └── diagnosis ←───────┘
```

### 路由规则

1. **用户在报告 bug、错误、异常、"不对"、"出问题了"** → 加载 `diagnosis`
2. **用户明确要求修改 Skill 系统本身** → 加载 `skill-creator`
3. **其他所有情况，一律加载 `discovery`**

Discovery 是唯一入口，负责理解用户意图后引导进入正确的下一阶段。

## Skills 清单

### 核心阶段 Skills

| Skill | 调用时机 | 职责 |
|-------|----------|------|
| discovery | 新需求/新想法/不确定 | 通过提问拆解，输出结构化理解 |
| planning | 目标清楚，路径不清楚 | 设计可行的执行方案 |
| execution | 目标和路径都清楚 | 通过 Subagent 高效执行 |
| diagnosis | 出现问题/错误/偏差 | 找到根因并解决 |
| deploy | 部署上线 | 部署与环境同步 |
| verification | 部署完成后 | 验证部署结果 |
| documentation-update | 功能完成后 | 确保文档与代码一致 |

### 功能增强 Skills

| Skill | 职责 |
|-------|------|
| skill-creator | 创建和更新 Skill |
| skills-updater | 检查和更新已安装的 Skills |
| key-reader | 安全读取外部 API 密钥 |
| smart-fetch | 反爬站点的智能网页抓取 |
| ui-ux-pro-max | UI/UX 设计增强 |
| frontend-design | 前端组件开发 |
| vue-best-practices | Vue 3 最佳实践 |
| github-to-skills | 将 GitHub 项目转化为 Skill |
| write-xiaohongshu | 小红书笔记创作 |
| chroma | Chroma 向量数据库集成 |

## 行为规范

### 绝对铁律

- **所有代码撰写必须通过 Task 工具调用 Subagent 完成。没有任何例外。**
- 主 Agent 专注于**思考和调度**，禁止在 Execution 阶段直接使用 Edit/Write 工具
- Discovery 是唯一入口，不要自作主张跳过 discovery 直接进 planning 或 execution

### 反合理化检查

如果你脑子里出现以下想法，立刻停下：

| 想法 | 真相 |
|------|------|
| "这次可以例外" | 不可以。例外一开就停不住 |
| "任务太简单不需要走流程" | 简单任务走流程成本极低，不走流程出错成本极高 |
| "先做着看" | 先做着看 = 返工。先想清楚再做 |
| "差不多就行了" | 差不多 = 没做完 |
| "就改一行，不用开子代理" | 一行也是代码。主Agent 碰代码 = 违规 |

## 环境配置：glo.env

`glo.env` 是整个系统的密钥和基础设施配置中心，不入库（含敏感信息）。需要在 `~/.claude/glo.env` 中配置各 API 密钥和服务器信息。

## 项目结构

```
~/.claude/
├── CLAUDE.md              # 核心行为指令
├── glo.env                # 密钥配置（不入库）
├── README.md              # 本文档
├── skills/                # Skill 目录
│   ├── discovery/
│   ├── planning/
│   ├── execution/
│   ├── diagnosis/
│   ├── deploy/
│   ├── verification/
│   ├── documentation-update/
│   ├── key-reader/
│   ├── smart-fetch/
│   ├── ui-ux-pro-max/
│   ├── skill-creator/
│   └── ...
├── scripts/               # 工具脚本
│   └── scan_contracts.py  # 项目进度扫描
├── projects/              # 项目状态存储
├── tasks/                 # 任务追踪
└── plans/                 # 计划文件
```

## 安装

```bash
git clone <repo-url> ~/.claude
# 创建 glo.env 并填入你的密钥
touch ~/.claude/glo.env
```

## 使用流程

1. **开始新任务**：Claude 会自动加载 CLAUDE.md，根据用户输入路由到对应 Skill
2. **遵循 Skill 指导**：每个 Skill 都有详细的执行指南，严格按照指南执行
3. **阶段推进**：当前阶段完成后，Skill 会引导用户选择下一步
4. **沉淀经验**：任务完成后，如有改进建议，使用 `skill-creator` 更新相关 Skill
