# 后端开发模式

> 供Subagent执行后端开发任务时参考

## API设计

### RESTful规范
```
GET    /api/resources          # 列表
GET    /api/resources/:id      # 单个
POST   /api/resources          # 创建
PUT    /api/resources/:id      # 替换
PATCH  /api/resources/:id      # 更新
DELETE /api/resources/:id      # 删除
```

### 查询参数
```
GET /api/resources?status=active&sort=name&limit=20&offset=0
```

---

## 架构模式

### Repository模式
- 抽象数据访问逻辑
- 定义接口，实现可替换
- 便于测试和维护

### Service层模式
- 业务逻辑与数据访问分离
- Service调用Repository
- 处理复杂业务规则

### 中间件模式
- 请求/响应处理管道
- 认证、日志、错误处理
- 可组合、可复用

---

## 数据库优化

### 查询优化
- 只选择需要的列
- 使用索引
- 避免SELECT *

### N+1问题
```typescript
// ❌ N+1查询
for (const item of items) {
  item.related = await getRelated(item.id)
}

// ✅ 批量查询
const relatedMap = await getRelatedBatch(items.map(i => i.id))
items.forEach(item => item.related = relatedMap.get(item.id))
```

---

## 缓存策略

### Cache-Aside模式
1. 先查缓存
2. 缓存未命中则查数据库
3. 更新缓存
4. 返回数据

### 缓存失效
- 设置合理的TTL
- 数据变更时主动失效
- 考虑缓存穿透/雪崩

---

## 错误处理

### 自定义错误类
- 包含状态码
- 包含用户友好消息
- 区分操作错误和程序错误

### 重试机制
- 指数退避
- 最大重试次数
- 只重试可恢复错误

---

## 认证授权

### JWT验证
- 验证签名
- 检查过期时间
- 提取用户信息

### RBAC
- 定义角色和权限
- 检查用户角色
- 验证操作权限

---

## 速率限制

- 基于IP或用户
- 滑动窗口算法
- 返回429状态码
- 敏感操作更严格
