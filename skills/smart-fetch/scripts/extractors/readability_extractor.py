# -*- coding: utf-8 -*-
"""通用正文提取器：使用 readability-lxml 自动识别正文区域（兜底方案）"""

from readability import Document
from markdownify import markdownify as md

from .base import Article


class ReadabilityExtractor:
    """基于 readability 算法的通用内容提取器"""

    def extract(self, html: str, url: str = "") -> Article:
        doc = Document(html)

        # 提取正文 HTML 并转为 Markdown
        summary_html = doc.summary()
        content = md(summary_html, strip=["img", "script", "style"]).strip()

        return Article(
            title=doc.title().strip(),
            content=content,
            source_url=url,
            fetch_method="readability",
        )
