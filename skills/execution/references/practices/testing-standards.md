# 测试规范

> 供Subagent执行测试相关任务时的硬性约束

**覆盖率要求：≥80%（单元+集成+E2E 合计）**

---

## MUST DO

- [ ] 测试先写，代码后写——不得先写实现再补测试
- [ ] RED 阶段必须验证测试确实失败（防止写出永远通过的测试）
- [ ] GREEN 阶段只写最小实现，不做提前优化
- [ ] MUST mock 所有外部依赖（API、数据库、文件系统、第三方服务）
- [ ] MUST 测试 happy path 和 error case（每个功能至少各一个）
- [ ] MUST 测试边界条件（空值、零值、极大值、类型边界）
- [ ] 每个测试遵循 AAA 模式（Arrange-Act-Assert）
- [ ] 测试命名描述用户行为：`应该在邮箱无效时返回400`

## MUST NOT DO

- [ ] MUST NOT 创建顺序依赖的测试——每个测试独立运行
- [ ] MUST NOT 测试实现细节（测试行为，不测试内部状态）
- [ ] MUST NOT 在测试中使用真实外部服务
- [ ] MUST NOT 共享可变状态（每个测试自己 setup/teardown）

---

## 测试类型与范围

| 类型 | 目标 | 速度要求 |
|------|------|----------|
| 单元测试 | 独立函数、纯逻辑、工具函数 | <50ms/个 |
| 集成测试 | API端点、数据库操作、服务交互 | <500ms/个 |
| E2E测试 | 关键用户流程、完整工作流 | <10s/个 |

---

## 测试结构

```typescript
describe('功能模块', () => {
  beforeEach(() => { /* 隔离的测试环境 */ })
  afterEach(() => { /* 清理 */ })

  it('应该在正常输入时返回预期结果', () => {
    // Arrange
    const input = createTestInput()
    // Act
    const result = doSomething(input)
    // Assert
    expect(result).toEqual(expected)
  })

  it('应该在无效输入时抛出错误', () => {
    expect(() => doSomething(null)).toThrow()
  })
})
```

---

## 选择器规范（E2E）

```typescript
// ✅ 语义化选择器
await page.click('button:has-text("Submit")')
await page.click('[data-testid="submit-btn"]')

// ❌ 脆弱的选择器
await page.click('.css-class-xyz')
```

---

## 文件组织

```
src/
├── components/
│   └── Button/
│       ├── Button.tsx
│       └── Button.test.tsx      # 单元测试
├── app/api/
│   └── users/
│       ├── route.ts
│       └── route.test.ts        # 集成测试
└── e2e/
    └── auth.spec.ts             # E2E测试
```
