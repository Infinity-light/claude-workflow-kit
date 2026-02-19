# TypeScript开发模式

> 供Subagent执行TypeScript开发任务时参考

## 类型定义

### 接口vs类型别名
```typescript
// 接口：可扩展，适合对象结构
interface User {
  id: string
  name: string
}

// 类型别名：适合联合类型、工具类型
type Status = 'active' | 'inactive' | 'pending'
type UserWithStatus = User & { status: Status }
```

### 泛型
```typescript
// 函数泛型
function first<T>(arr: T[]): T | undefined {
  return arr[0]
}

// 接口泛型
interface ApiResponse<T> {
  success: boolean
  data?: T
  error?: string
}
```

---

## 类型守卫

### typeof守卫
```typescript
function process(value: string | number) {
  if (typeof value === 'string') {
    return value.toUpperCase()
  }
  return value * 2
}
```

### 自定义守卫
```typescript
function isUser(obj: unknown): obj is User {
  return typeof obj === 'object' && obj !== null && 'id' in obj
}
```

---

## 工具类型

### 常用内置类型
- `Partial<T>` - 所有属性可选
- `Required<T>` - 所有属性必需
- `Pick<T, K>` - 选择部分属性
- `Omit<T, K>` - 排除部分属性
- `Record<K, V>` - 键值对映射

### 示例
```typescript
type CreateUserDto = Omit<User, 'id' | 'createdAt'>
type UpdateUserDto = Partial<CreateUserDto>
```

---

## 严格模式最佳实践

### 避免any
```typescript
// ❌ 避免
function process(data: any) { }

// ✅ 使用unknown + 类型守卫
function process(data: unknown) {
  if (isValidData(data)) { }
}
```

### 非空断言谨慎使用
```typescript
// ❌ 危险
const value = map.get(key)!

// ✅ 安全
const value = map.get(key)
if (!value) throw new Error('Not found')
```

---

## 模块组织

### 类型导出
```typescript
// types/user.ts
export interface User { }
export type UserRole = 'admin' | 'user'

// 使用
import type { User, UserRole } from '@/types/user'
```

### 桶文件
```typescript
// types/index.ts
export * from './user'
export * from './market'
export * from './api'
```
