# 编码规范

> 供Subagent执行编码任务时的硬性约束

## MUST DO

- [ ] 文件大小：200-400行典型，800行硬上限。超过则拆分
- [ ] 函数长度：<50行。超过则提取子函数
- [ ] 嵌套层级：<4层。超过则用 early return / 提取函数
- [ ] 不可变优先：用 spread 替代 mutation（`{...obj}` / `[...arr]`）
- [ ] 禁止 magic numbers：所有数字常量必须命名（`const MAX_RETRIES = 3`）
- [ ] 命名描述性：变量用名词，函数用动词+名词，布尔用 is/has/can 前缀
- [ ] 类型安全：禁止 `any`，用 `unknown` + 类型守卫替代
- [ ] 错误处理：所有 async 操作必须 try/catch，错误信息包含上下文
- [ ] 并行执行：无依赖的 async 操作用 `Promise.all`
- [ ] 每类功能必须有 Golden Example 参照——先找项目中已有的同类代码，保持风格一致

## MUST NOT DO

- [ ] 不得硬编码密钥、密码、token
- [ ] 不得使用 `var`（用 `const` / `let`）
- [ ] 不得直接修改参数对象（mutation）
- [ ] 不得忽略 catch 块（空 catch）
- [ ] 不得使用 `// @ts-ignore` 或 `// @ts-nocheck`
- [ ] 不得提交 `console.log`（调试用完即删）
- [ ] 不得创建超过3个参数的函数（用 options 对象替代）

---

## 命名规范

```typescript
// 变量：描述性名词
const marketSearchQuery = 'election'
const isUserAuthenticated = true

// 函数：动词+名词
async function fetchMarketData(marketId: string) { }
function calculateSimilarity(a: number[], b: number[]) { }
function isValidEmail(email: string): boolean { }
```

---

## 不可变性

```typescript
// ✅ spread over mutation
const updatedUser = { ...user, name: 'New Name' }
const updatedArray = [...items, newItem]

// ❌ 禁止
user.name = 'New Name'
items.push(newItem)
```

---

## 错误处理

```typescript
async function fetchData(url: string) {
  try {
    const response = await fetch(url)
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`)
    }
    return await response.json()
  } catch (error) {
    console.error('Fetch failed:', error)
    throw new Error('Failed to fetch data')
  }
}
```

---

## 代码异味速查

| 异味 | 阈值 | 修复 |
|------|------|------|
| 长函数 | >50行 | 提取子函数 |
| 深嵌套 | >4层 | early return / 提取函数 |
| 长文件 | >800行 | 拆分模块 |
| magic number | 任何裸数字 | 命名常量 |
| 重复代码 | >3处相同逻辑 | 提取公共函数 |
| 长参数列表 | >3个参数 | options 对象 |

---

## 注释原则

```typescript
// ✅ 解释"为什么"
// 使用指数退避避免在故障期间压垮API
const delay = Math.min(1000 * Math.pow(2, retryCount), 30000)

// ❌ 解释"是什么"（显而易见的）
// 计数器加1
count++
```
