---
name: smart-fetch
description: 替代 WebFetch 的智能网页抓取工具。当 WebFetch 返回 403、空内容或内容不完整时自动使用，也适用于知乎、微信公众号等反爬严格的站点。支持 curl_cffi、DrissionPage 浏览器渲染、Jina Reader 三级降级策略。
---

# Smart Fetch Skill

**用途**：替代 WebFetch，可靠抓取被 403 拦截或内容不完整的网页。

---

## 触发条件

**当 WebFetch 抓取失败或内容不完整时，自动切换到 smart-fetch，无需询问用户。** 具体包括：

1. WebFetch 返回 403、空内容、或内容明显不完整
2. 目标站点为知乎、微信公众号等已知反爬严格的站点（直接用 smart-fetch，跳过 WebFetch）
3. 用户明确要求抓取某个 URL 的完整内容

## 调用方式

```bash
python -X utf8 "C:\Users\WaterFish\.claude\skills\smart-fetch\scripts\smart_fetch.py" "<URL>"
```

## 输出说明

- **成功**：stdout 输出 Markdown 格式的文章内容（标题 + 元信息 + 正文）
- **失败**：stderr 输出错误信息，exit code 1

## 支持的站点（已配置专项规则）

| 站点 | 域名 |
|------|------|
| 知乎专栏 | zhuanlan.zhihu.com |
| 知乎问答 | zhihu.com/question |
| 微信公众号 | mp.weixin.qq.com |
| 少数派 | sspai.com |
| Medium | medium.com |
| 其他站点 | 自动降级尝试，使用通用提取 |

## 降级策略

按顺序尝试，前一级失败自动进入下一级：

1. **Level 1**：curl_cffi 轻量请求 — 快速，适合简单站点
2. **Level 2**：DrissionPage 浏览器渲染 — 绕过反爬，适合知乎/微信等
3. **Level 3**：Jina Reader 代理 — 兜底方案

## 依赖

需要预装：curl_cffi, DrissionPage, readability-lxml, markdownify, lxml

```bash
pip install -r skills/smart-fetch/scripts/requirements.txt
```

## 注意事项

- 浏览器策略（Level 2）首次运行较慢（约 5-8 秒），后续会快一些
- 仅用于学习研究目的，请遵守目标站点的使用条款
- 如需添加新站点规则，编辑 `scripts/site_rules.json`
