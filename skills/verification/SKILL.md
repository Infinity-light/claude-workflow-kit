---
name: verification
description: 部署后验证阶段。当 deploy 完成后触发，使用 agent-browser 子代理对生产环境做针对性验证，验证通过后加载 documentation-update skill 更新文档。当用户说"验证"、"verify"、"检查部署结果"、"测一下线上"时触发。
---

## 铁律

不验证的部署等于没部署。验证内容由本轮变更决定，不是固定清单。

## 常见借口（都是错的）

| 你可能会想 | 为什么是错的 |
|-----------|------------|
| "刚才本地测过了，线上肯定没问题" | 本地和生产环境不同，NEXT_PUBLIC 构建时注入、Docker 网络、DNS 都可能出问题 |
| "只改了一行文案，不用验证" | 一行改动也可能因为构建缓存、字段名不匹配等原因在线上表现不同 |
| "验证太慢，先跳过" | 不验证 → 用户发现问题 → 诊断 + 修复 + 重新部署，更慢 |

## 核心流程

### 1. 确认部署状态

检查 CI/CD 是否成功完成：
```bash
gh run list --limit 1
```
- 成功 → 继续
- 失败/进行中 → 等待或排查

### 2. 收集本轮变更范围

从以下来源推导验证重点：
- `git log`：从上次部署到现在的 commits
- TaskList：本轮完成的任务描述
- 变更文件列表：`git diff --name-only <上次部署commit>..HEAD`

基于变更范围，确定：
- **变更验证点**：本轮改了什么，就验证什么
- **冒烟验证点**：核心流程快速过一遍（登录、主要页面可访问）

### 3. 调度 agent-browser 子代理验证

启动 Task 子代理，使用 agent-browser skill 执行验证：
- 将变更验证点和冒烟验证点作为测试指令传入
- 子代理使用 `agent-browser open/snapshot/screenshot` 逐一验证
- 子代理只返回发现的问题，无问题则返回"全部通过"

**子代理 prompt 必须包含**：
- 生产环境 URL
- 测试账号（如需登录）
- 本轮变更的具体验证点
- 冒烟验证的页面列表

### 4. 处理验证结果

**全部通过** → 加载 `documentation-update` skill，更新项目文档
**发现问题** → 用 AskUserQuestion 展示问题清单，选项：
- "全部修复"（推荐）→ 进入 diagnosis
- "部分修复" → 用户选择哪些需要修
- "暂不处理" → 记录问题，进入文档更新

### 5. 文档更新（子模块）

验证通过后，加载 documentation-update skill：
```
Skill(skill: "documentation-update")
```
按该 skill 的流程更新项目 CLAUDE.md，确保文档与已验证的线上行为一致。

## 阶段结束

文档更新完成后，用 AskUserQuestion 向用户确认：

选项必须包含：
- "本轮工作完成"
- "需要补充任务" → 回到 execution
- "暂停"
