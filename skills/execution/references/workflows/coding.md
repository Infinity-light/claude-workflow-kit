# Coding Workflow

## 1. 执行前：上下文探索

1. **项目结构扫描**
   - 探索项目根目录，识别技术栈（语言、框架、构建工具、包管理器）
   - 如果项目有 `.claude/CLAUDE.md`，优先读取——其中的架构约定和技术规范是最高优先级约束

2. **加载匹配规范**
   - 扫描 `practices/` 目录，找到与当前技术栈和任务类型匹配的规范文件并读取
   - 没有精确匹配时，选最接近的；完全没有时，按通用工程常识执行

3. **Skill 按需加载**
   - 涉及前端 UI 开发 → 加载 `frontend-design` Skill
   - 涉及安全敏感操作 → 读取 `practices/security-checklist.md`

## 2. TDD 串行循环

采用 RED → GREEN → REFACTOR 串行模式，不并行隔离。

```
┌─────────────────────────────────────────────┐
│  Subagent-1: 写测试（RED）                    │
│  - 读取 practices/ 中匹配的规范               │
│  - 读取 practices/testing-standards.md        │
│  - 写测试 → 运行测试 → 确认失败               │
│  - 产出：失败的测试文件                        │
├─────────────────────────────────────────────┤
│  Subagent-2: 写实现（GREEN）                  │
│  - 读取 Subagent-1 产出的测试文件              │
│  - 读取 practices/ 中匹配的规范               │
│  - 写实现 → 运行测试 → 确认通过               │
│  - 失败则自行修复，连续失败 2 次 → 报告主Agent │
│  - 产出：让测试通过的最小实现                   │
├─────────────────────────────────────────────┤
│  Subagent-3: REFACTOR（可选）                 │
│  - 读取 practices/coding-standards.md          │
│  - 重构 → 运行测试 → 确认仍通过               │
└─────────────────────────────────────────────┘

主Agent 只负责调度和判断流程走向，不直接执行任何具体操作。
连续失败 2 次由 Subagent 报告后，主Agent 决定是否转 diagnosis 阶段。
```

对于简单修改或非核心逻辑，可跳过 TDD 直接实现，但必须在实现后补验证。

## 3. 验证流程

按顺序执行，任一阶段失败则停止修复后重来：

1. 构建验证
2. 类型检查
3. Lint 检查
4. 测试套件 — 覆盖率标准参照 `practices/testing-standards.md`
5. 安全扫描 — 检查项参照 `practices/security-checklist.md`
6. Diff 审查 — 检查是否有意外变更、遗漏的边界情况
7. 代码审查 — 启动审查子代理，检查命名规范、代码结构、边界情况、安全隐患。审查 prompt 中指定读取 `practices/coding-standards.md` 和 `practices/security-checklist.md`

E2E 验证在关键功能变更时追加（核心用户流程、关键业务路径、权限边界）。

## 4. Subagent 调度：约束传递

调度 Subagent 时，**必须在 Task prompt 中显式指定需要读取的约束文件**，让规范在 Subagent 内部生效。

模板：
```
执行 [具体任务描述]。

开始前先读取以下文件并严格遵循：
- practices/[匹配的规范文件]
- [项目 .claude/CLAUDE.md 中的相关约定，如有]

[具体的输入、输出要求]
```

不要假设 Subagent 会自动继承主 Agent 的上下文——约束必须显式传递。
