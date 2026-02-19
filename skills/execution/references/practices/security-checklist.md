# 安全检查清单

> 供Subagent执行涉及安全相关任务时的硬性约束

## 红旗清单（自动扫描项）

扫描代码时按以下分级报告，只报告置信度 >80% 的问题：

### CRITICAL（必须立即修复）
- [ ] 硬编码密钥/凭证（API key、password、token、secret 出现在源码中）
- [ ] SQL 注入（字符串拼接构建查询）
- [ ] 命令注入（用户输入直接传入 exec/spawn）
- [ ] 未加密存储敏感数据

### HIGH（提交前必须修复）
- [ ] XSS 漏洞（未转义的用户输入渲染到 HTML）
- [ ] 不安全的反序列化
- [ ] 缺少认证检查的敏感端点
- [ ] Token 存储在 localStorage（应用 httpOnly cookie）
- [ ] 缺少 CSRF 防护的状态变更操作

### MEDIUM（应在当前迭代修复）
- [ ] 缺少输入验证（用户输入未经 schema 验证）
- [ ] 缺少速率限制
- [ ] 过于宽泛的 CORS 配置
- [ ] 错误信息泄露内部细节（堆栈、路径、版本）
- [ ] 缺少安全响应头（CSP、X-Frame-Options）

### LOW（记录并计划修复）
- [ ] console.log 残留（可能泄露数据）
- [ ] 过期依赖（已知漏洞）
- [ ] 缺少 Subresource Integrity

---

## 密钥管理

```typescript
// ❌ CRITICAL
const API_KEY = 'sk-abc123...'
const query = `SELECT * FROM users WHERE email = '${userEmail}'`

// ✅ 正确
const API_KEY = process.env.API_KEY
if (!API_KEY) throw new Error('API_KEY not configured')
await db.query('SELECT * FROM users WHERE email = $1', [userEmail])
```

---

## 输入验证

- 所有用户输入使用 schema 验证（推荐 zod）
- 白名单验证（非黑名单）
- 文件上传限制大小、类型、扩展名
- 错误信息不泄露内部细节

---

## XSS 防护

- 用户 HTML 内容使用 DOMPurify 清理
- 配置 CSP 头
- 避免 `dangerouslySetInnerHTML`（除非内容已清理）
- React 默认转义——但 `href`、`src` 等属性仍需手动验证

---

## 认证与授权

- Token 存储在 httpOnly cookie（Secure + SameSite=Strict）
- 合理的过期时间
- 敏感操作前验证权限
- Supabase 项目启用 RLS

---

## 部署前检查

```bash
# 依赖漏洞
npm audit

# 硬编码密钥扫描
grep -rn "sk-\|api_key\|password\s*=" --include="*.ts" --include="*.js" .

# console.log 残留
grep -rn "console.log" --include="*.ts" --include="*.tsx" src/
```

- [ ] 无硬编码密钥
- [ ] 所有输入已验证
- [ ] 查询已参数化
- [ ] XSS/CSRF 防护到位
- [ ] 认证授权正确实现
- [ ] 速率限制启用
- [ ] HTTPS 强制
- [ ] 安全头配置
- [ ] 日志无敏感数据
- [ ] 依赖无已知漏洞
