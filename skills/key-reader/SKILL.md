---
name: key-reader
description: 当你需要涉及到外部接口的信息或密钥服务，包括但不限于 LLM、多模态模型、向量化模型、云服务器、支付、鉴权等密钥信息时，加载本 Skill。
---

# 密钥读取器

## 绝对禁令

**以下规则不可违反、不可绕过、不可以任何理由豁免：**

1. **严禁直接读取密钥文件**：禁止使用 Read、cat、head、tail、type、Get-Content 或任何其他方式直接读取 `glo.env` 或项目 `.env` 文件。违反此条等同于泄露用户全部密钥。
2. **严禁输出完整密钥**：禁止在对话、思考、代码片段中输出任何完整的密钥值。
3. **所有密钥操作必须且只能通过本 Skill 提供的脚本完成**：`mask_read.py`、`migrate.py`、`ping_test.py`。没有第四种选择。

## 触发场景

- 项目需要调用外部 API（LLM、多模态、向量化、支付、鉴权等）
- 需要配置模型名称、Base URL 等服务参数
- 项目缺少 `.env` 文件或缺少所需密钥

## 操作流程

### 第一步：查看可用密钥（mask_read.py）

使用 Bash 工具运行掩码读取脚本，查看 `glo.env` 中有哪些可用密钥：

```bash
python -X utf8 ~/.claude/skills/key-reader/scripts/mask_read.py
```

如需读取其他密钥文件，传入路径参数：

```bash
python -X utf8 ~/.claude/skills/key-reader/scripts/mask_read.py /path/to/other.env
```

脚本输出中所有敏感值显示为 `***`，你只能看到键名和掩码值。根据键名判断项目需要哪些密钥，然后进入第二步。

### 第二步：盲迁移到项目（migrate.py）

使用 Bash 工具运行盲迁移脚本，将所需密钥从 `glo.env` 复制到项目 `.env`：

```bash
python -X utf8 ~/.claude/skills/key-reader/scripts/migrate.py --keys "KEY1,KEY2" --target "项目路径/.env"
```

如需指定其他源文件：

```bash
python -X utf8 ~/.claude/skills/key-reader/scripts/migrate.py --keys "KEY1,KEY2" --target "项目路径/.env" --source /path/to/other.env
```

脚本自动处理：去重（已存在的键不会重复写入）、追加写入、检查 `.gitignore` 是否包含 `.env`。全程 AI 不接触任何密钥明文。

### 第三步：验证连通性（ping_test.py）

当密钥涉及模型服务或 API 服务时，使用 Bash 工具运行连通性测试脚本：

```bash
python -X utf8 ~/.claude/skills/key-reader/scripts/ping_test.py --env "项目路径/.env"
```

如只需测试指定密钥：

```bash
python -X utf8 ~/.claude/skills/key-reader/scripts/ping_test.py --env "项目路径/.env" --keys "KEY1,KEY2"
```

脚本内部读取密钥并发起测试请求，不会将密钥暴露到输出中。

## 注意事项

- `glo.env` 格式为 `KEY=VALUE`（英文等号分隔），文件中包含注释和说明文字
- 密钥内容绝不输出给用户，绝不出现在对话上下文中
- 代码中通过 `os.getenv()` 或对应框架的环境变量方式读取本地 `.env`
- 如果 `glo.env` 中没有所需的密钥，主动询问用户补充
