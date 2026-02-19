分析以下工具调用记录，提取可复用的行为模式。

## 观察数据

{{OBSERVATIONS}}

## 模式检测

寻找以下模式（需要 3+ 次出现）：
1. 重复工作流：相同的工具序列被多次使用
2. 错误修复模式：工具输出包含错误，随后被修复
3. 工具偏好：持续选择某种工具而非替代方案
4. 用户纠正：撤销/重做模式

## 输出格式

对每个检测到的模式，输出一个 INSTINCT 块（用 === 分隔）：

===INSTINCT===
id: kebab-case-id
trigger: 触发条件
confidence: 0.3-0.85
domain: workflow|code-style|debugging|testing|tool-usage
title: 标题
action: 触发时应该做什么
evidence: 观察到N次，模式描述
===END===

置信度：1-2次=0.3，3-5次=0.5，6-10次=0.7，11+=0.85

## 规则

- 保守：只为清晰、重复的模式创建
- 跳过琐碎模式（如"用 Read 读文件"）
- 如果没有有意义的模式，只输出：NO_PATTERNS_DETECTED
