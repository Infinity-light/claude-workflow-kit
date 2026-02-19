---
name: self-evolve
description: 当用户想查看或应用自迭代系统积累的直觉时使用。将成熟直觉演进为 Skill 改进。
---

# 自演进阶段

## 识别信号

- 用户说"看看有什么可以改进的"、"检查直觉"、"演进"
- 直觉系统积累了足够多的成熟直觉（confidence >= 0.75）

## 核心流程

### 1. 诊断现状

使用以下代码检查直觉状态：

```python
import sys; sys.path.insert(0, r'C:\Users\WaterFish\.claude\hooks')
from memory_store import MemoryStore
store = MemoryStore()
active = store.get_active_instincts()
mature = store.get_mature_instincts()
```

向用户报告：
- 活跃直觉总数及各领域分布
- 成熟直觉（confidence >= 0.75 且 evidence >= 3）列表
- 每条成熟直觉的 trigger、action、confidence

### 2. 聚类分析

将成熟直觉按 domain 分组，对每个聚类：
- 检查是否已有对应的 Skill（在 `skills/` 目录下搜索）
- 如果有 → 生成**修改提案**（具体改哪个文件的哪个部分）
- 如果没有 → 生成**新建提案**（新 Skill 的名称和内容大纲）

### 3. 提案展示

用 AskUserQuestion 向用户展示每个提案，选项：
- **应用** — 立即写入 Skill 文件
- **修改** — 用户调整后再写入
- **跳过** — 暂不处理，直觉保持 active

### 4. 执行写入

用户确认后：
- 修改或创建对应的 Skill 文件
- 将已演进的直觉标记为 archived：`store.archive_instinct(id, skill_ref)`
- 写入每日日志记录本次演进

## 输出

- 演进报告：处理了多少直觉，生成了多少提案，应用了多少
- 建议下次检查的时间（基于直觉积累速度）

## 注意事项

- **绝不自动修改 Skill**，必须经过用户确认
- 提案应具体到文件路径和修改内容，不要泛泛而谈
- 优先改进现有 Skill，而非创建新 Skill
