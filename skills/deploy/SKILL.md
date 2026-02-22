---
name: deploy
description: 部署与环境同步。首次部署用 `deploy-setup all`，后续 .env 变更用 `deploy-setup sync-env`。当用户说"部署"、"deploy"、"上线"、"配置CI/CD"、"同步环境变量"、"更新secret"、"sync env"时触发。
---

## 铁律

没有通过 CI 不上生产。绝对禁止绕过 deploy-setup 手动部署。

## 常见借口（都是错的）

| 你可能会想 | 为什么是错的 |
|-----------|------------|
| "CI 太慢了，先手动部署" | 手动部署导致服务器状态与 CI/CD 不一致，后续自动部署会覆盖 |
| "只是改了个小配置，不用走 CI" | 小改动出大事故的概率不低。流程保护你 |
| "deploy-setup 有 bug，我先绕过" | 工具有问题就修工具，绕过工具 = 放弃所有内置的健康检查和回滚 |

# Deploy

一次性设置 CI/CD，之后 git push 自动部署。支持 Flask、Django、FastAPI、NestJS、Next.js、Nuxt.js、Vue SPA、React SPA。

## ⛔ 禁止手动部署

**绝对禁止**绕过 `deploy-setup` 工具，手动执行 scp、ssh、docker 等命令进行部署。

无论出于什么原因（"工具太慢"、"只是临时部署"、"先手动搞一下"），都不允许。手动部署会导致：
- 服务器状态与 CI/CD 不一致，后续自动部署覆盖手动配置
- 无法复现的部署过程，出问题无法回溯
- 跳过了工具内置的健康检查和回滚机制

**如果 deploy-setup 工具本身有问题**，应该修复工具或用子命令单步排查，而不是绕过它。

## 前置条件

- 项目代码已就绪，有可运行的应用
- 项目已关联 GitHub 远程仓库（`git remote -v` 可见），没有则先 `gh repo create`
- **Git remote 必须使用 SSH 格式**（`git@github.com:user/repo.git`），不用 HTTPS。创建仓库时用 `gh repo create --source=. --push` 会自动使用 SSH（前提是 `gh auth login --git-protocol ssh`）
- **全链路约束已在 Planning 阶段探测通过**（SSH 可连、域名已解析、gh CLI 已认证等）

## 执行

```bash
deploy-setup all
```

一条命令完成全部流程：检测项目 → 交互收集配置 → 生成 CI/CD 文件 → DNS 检查 → SSH 初始化服务器 → 配置 GitHub Secrets → git push → 等待 Actions 完成。

如果命令不可用：`node "D:\TechWork\自由发散地\deploy-setup\dist\cli.js" all`

成功标志：输出"部署完成! 后续 git push 即自动部署。"

## 环境变量同步

项目 `.env` 新增/删除变量后，用 `sync-env` 同步到 deploy.yml 和 GitHub Secrets：

```bash
# 查看差异（不修改）
deploy-setup sync-env --dry-run

# 执行同步（交互式分类 secret/hardcoded）
deploy-setup sync-env

# 跳过交互，用正则自动分类（匹配 secret/password/key/token/api 的归 secret）
deploy-setup sync-env --yes

# 同步并自动推送新 secrets 到 GitHub（适合 CI 或脚本调用）
deploy-setup sync-env --yes --push-secrets -e server/.env
```

| 选项 | 作用 |
|------|------|
| `-d, --dir <dir>` | 项目目录（默认 cwd） |
| `-e, --env-file <path>` | 从文件读取密钥值 |
| `-y, --yes` | 跳过交互，自动用正则分类 secret/hardcoded |
| `--dry-run` | 仅显示差异，不修改 |
| `--push-secrets` | 自动推送新 secrets 到 GitHub |

sync-env 会自动扫描 multi-dir 项目的 `server/.env`，无需手动指定路径。

## 失败时单步排查

`all` 中途失败时，用子命令从断点继续：

| 命令 | 作用 |
|------|------|
| `deploy-setup init` | 重新生成配置文件 |
| `deploy-setup check-dns` | 单独检查 DNS |
| `deploy-setup setup-server` | 单独初始化服务器 |
| `deploy-setup setup-secrets` | 单独配置 Secrets |

## 错误速查

| 症状 | 原因 | 解决 |
|------|------|------|
| gunicorn app:app 失败 | Flask 工厂模式 | startCmd 改为 run:app |
| .env not found | 服务器无 .env | 重跑 setup-server |

| SSH connection refused | 密钥/端口/防火墙 | 检查 sshKeyPath、安全组 |
| health check failed | 容器崩溃 | SSH 到服务器 `docker logs` |
| 容器内访问不到宿主机 DB | DB 在宿主机，容器用 bridge 网络 | compose 改用 network_mode: host |
| bash 报语法错误 / unexpected token | .sh 文件含 CRLF 行尾 | 用 dos2unix 转换或重新生成 |
| Dockerfile COPY 失败 / npm ci 找不到 package.json | 项目为多目录结构，模板不匹配 | 重跑 init，确认检测到 multi-dir |
| Secrets 值为空 / .env 变量缺失 | setup-secrets 未设置业务密钥 | 重跑 setup-secrets，确认所有 key |
| docker compose build 失败 | Dockerfile 或源码问题 | SSH 到服务器查看构建日志，检查 Dockerfile |
| SSH handshake timeout | 密钥格式不兼容 (OpenSSH vs PEM) | 用 ssh-keygen -p -m PEM 转换，或用 ed25519 密钥 |
| .env 新增变量未生效 | 变量未同步到 Secrets 和 deploy.yml | 运行 `deploy-setup sync-env --push-secrets` |

## 阶段结束

部署完成后，用 AskUserQuestion 向用户确认：

选项必须包含：
- "进入 Verification 验证部署结果"（推荐）
- "需要回滚"
- "跳过验证，结束任务"
