# -*- coding: utf-8 -*-
"""Smart Fetch 主入口：串联策略层与提取层，实现降级抓取流程."""

import sys
import os

# 确保能找到同级模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from strategies import LightFetch, BrowserFetch, ProxyFetch
from extractors import SiteRuleExtractor, ReadabilityExtractor, Article

STRATEGY_MAP = {
    "light": LightFetch,
    "browser": BrowserFetch,
    "proxy": ProxyFetch,
}

DEFAULT_CHAIN = ["light", "browser", "proxy"]


def fetch_and_extract(url: str) -> Article:
    """按降级顺序抓取 URL 并提取正文，返回 Article."""
    site_extractor = SiteRuleExtractor()
    rule = site_extractor.match(url)

    # 构建策略链
    if rule and rule.preferred_strategy:
        preferred = rule.preferred_strategy
        chain = [preferred] + [s for s in DEFAULT_CHAIN if s != preferred]
    else:
        chain = list(DEFAULT_CHAIN)

    # 构建 site_config（传给策略的额外配置）
    site_config = {}
    if rule:
        if rule.extra_headers:
            site_config["headers"] = rule.extra_headers
        if rule.wait_selector:
            site_config["wait_selector"] = rule.wait_selector

    # 遍历策略链，依次尝试
    for strategy_key in chain:
        cls = STRATEGY_MAP.get(strategy_key)
        if cls is None:
            continue
        try:
            strategy = cls()
            result = strategy.fetch(url, site_config)
            if not result.success:
                print(f"[{strategy.name}] 失败: status={result.status}", file=sys.stderr)
                continue

            # ProxyFetch 返回的已经是 Markdown，直接构造 Article
            if strategy_key == "proxy":
                return Article(
                    title="",
                    content=result.html,
                    source_url=url,
                    fetch_method=strategy.name,
                )

            # 其他策略返回 HTML，先尝试站点规则提取
            if rule and rule.content_selector:
                try:
                    article = site_extractor.extract(result.html, rule)
                    if article.content:
                        article.source_url = url
                        article.fetch_method = strategy.name
                        return article
                except Exception as e:
                    print(f"[站点规则提取] 失败: {e}", file=sys.stderr)

            # 兜底：readability 通用提取
            article = ReadabilityExtractor().extract(result.html, url)
            article.fetch_method = strategy.name
            return article

        except Exception as e:
            print(f"[{strategy_key}] 异常: {e}", file=sys.stderr)
            continue

    # 全部失败
    return Article(content="所有抓取策略均失败，请检查 URL 或网络连接。", source_url=url)


def main():
    if len(sys.argv) < 2:
        print("用法: python smart_fetch.py <URL>", file=sys.stderr)
        sys.exit(1)

    url = sys.argv[1]
    article = fetch_and_extract(url)

    if not article.fetch_method:
        print(article.content, file=sys.stderr)
        sys.exit(1)

    # 格式化输出到 stdout
    if article.title:
        print(f"# {article.title}\n")
    print(f"> 来源: {article.source_url}")
    print(f"> 抓取方式: {article.fetch_method}\n")
    print(article.content)


if __name__ == "__main__":
    main()
