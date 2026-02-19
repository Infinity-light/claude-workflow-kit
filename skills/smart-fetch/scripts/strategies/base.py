"""策略基类定义."""
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class FetchResult:
    """抓取结果."""
    html: str
    status: int
    method: str
    success: bool


class FetchStrategy(ABC):
    """抓取策略抽象基类."""

    @abstractmethod
    def fetch(self, url: str, site_config: dict = None) -> FetchResult:
        """执行抓取."""
        ...

    @property
    @abstractmethod
    def name(self) -> str:
        """策略名称."""
        ...
