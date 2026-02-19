# -*- coding: utf-8 -*-
"""站点规则提取器：根据已知站点的CSS选择器精准提取内容"""

import json
import os
import re
from typing import Optional
from urllib.parse import urlparse

from markdownify import markdownify as md

from .base import Article


class SiteRule:
    """单个站点的提取规则"""
    def __init__(self, config: dict):
        self.title_selector = config.get("title_selector", "")
        self.content_selector = config.get("content_selector", "")
        self.author_selector = config.get("author_selector", "")
        self.date_selector = config.get("date_selector", "")
        self.wait_selector = config.get("wait_selector", "")
        self.preferred_strategy = config.get("preferred_strategy", "")
        self.extra_headers = config.get("extra_headers", {})


class SiteRuleExtractor:
    """基于站点规则的内容提取器"""

    def __init__(self):
        rules_path = os.path.join(os.path.dirname(__file__), "..", "site_rules.json")
        with open(rules_path, "r", encoding="utf-8") as f:
            self._rules: dict = json.load(f)

    def match(self, url: str) -> Optional[SiteRule]:
        """根据URL域名匹配站点规则"""
        domain = urlparse(url).netloc
        path = urlparse(url).path

        for pattern, config in self._rules.items():
            # 支持域名匹配和路径前缀匹配
            if re.search(pattern, domain + path):
                return SiteRule(config)
        return None

    def extract(self, html: str, rule: SiteRule) -> Article:
        """用CSS选择器从HTML中提取内容"""
        from lxml.html import fromstring, tostring

        doc = fromstring(html)
        article = Article()

        # 提取标题
        if rule.title_selector:
            els = doc.cssselect(rule.title_selector)
            if els:
                article.title = els[0].text_content().strip()

        # 提取正文 HTML → Markdown
        if rule.content_selector:
            els = doc.cssselect(rule.content_selector)
            if els:
                raw_html = tostring(els[0], encoding="unicode")
                article.content = md(raw_html, strip=["img", "script", "style"]).strip()

        # 提取作者（可选）
        if rule.author_selector:
            els = doc.cssselect(rule.author_selector)
            if els:
                article.author = els[0].text_content().strip()

        # 提取日期（可选）
        if rule.date_selector:
            els = doc.cssselect(rule.date_selector)
            if els:
                article.publish_date = els[0].text_content().strip()

        return article
