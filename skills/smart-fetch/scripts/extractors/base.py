# -*- coding: utf-8 -*-
"""提取层数据模型与基类"""

from dataclasses import dataclass, field


@dataclass
class Article:
    """提取结果的统一数据模型"""
    title: str = ""
    content: str = ""  # Markdown 格式正文
    author: str = ""
    publish_date: str = ""
    source_url: str = ""
    fetch_method: str = ""  # 使用的抓取策略名称
