# React/前端开发模式

> 供Subagent执行前端开发任务时参考

## 组件模式

### 组合优于继承
- 使用children和插槽模式
- 创建可组合的小组件
- 避免深层继承

### 复合组件模式
- 使用Context共享状态
- 父组件管理状态，子组件消费
- 适用于Tabs、Accordion等

---

## 自定义Hooks

### useDebounce
```typescript
function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState(value)
  useEffect(() => {
    const handler = setTimeout(() => setDebouncedValue(value), delay)
    return () => clearTimeout(handler)
  }, [value, delay])
  return debouncedValue
}
```

### useToggle
```typescript
function useToggle(initial = false): [boolean, () => void] {
  const [value, setValue] = useState(initial)
  const toggle = useCallback(() => setValue(v => !v), [])
  return [value, toggle]
}
```

---

## 状态管理

### Context + Reducer
- 复杂状态使用useReducer
- 通过Context提供给子组件
- 避免prop drilling

### 状态更新原则
```typescript
// ✅ 函数式更新
setCount(prev => prev + 1)

// ❌ 直接引用（可能过期）
setCount(count + 1)
```

---

## 性能优化

### Memoization
- `useMemo`：缓存计算结果
- `useCallback`：缓存函数引用
- `React.memo`：缓存组件渲染

### 代码分割
```typescript
const HeavyComponent = lazy(() => import('./HeavyComponent'))

<Suspense fallback={<Loading />}>
  <HeavyComponent />
</Suspense>
```

### 虚拟化长列表
- 使用@tanstack/react-virtual
- 只渲染可见项
- 设置合理的overscan

---

## 表单处理

### 受控组件
- 状态驱动表单值
- onChange更新状态
- 提交前验证

### 验证模式
- 定义验证函数
- 收集错误信息
- 显示错误提示

---

## 错误边界

- 使用class组件捕获错误
- getDerivedStateFromError更新状态
- componentDidCatch记录日志
- 提供fallback UI

---

## 可访问性

### 键盘导航
- 处理ArrowUp/Down
- 处理Enter/Escape
- 设置正确的ARIA属性

### 焦点管理
- Modal打开时聚焦
- 关闭时恢复焦点
- 使用tabIndex控制
