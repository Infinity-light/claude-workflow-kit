---
id: search-read-edit-validate-cycle
trigger: "需要在代码库中定位、修改和验证代码时"
confidence: 0.7
domain: "workflow"
source: session-observation
last_observed: 2026-02-17
---

# 搜索-读取-编辑-验证循环

## Action
当需要修改代码时，按照 Grep → Read → Edit → Bash 的顺序执行。先搜索定位目标，读取完整上下文，进行编辑，最后用 Bash 验证结果。这个序列在记录中出现了2次完整循环。

## Evidence
- 观察到2次完整的 Grep→Read→Edit→Bash 序列（记录行1-4和5-8），表明这是一个标准的代码修改工作流。
