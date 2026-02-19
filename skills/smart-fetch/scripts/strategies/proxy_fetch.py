"""Level 3: 代理服务策略，使用 Jina Reader 获取 Markdown 内容."""
try:
    from curl_cffi import requests as cffi_requests
except ImportError:
    raise ImportError("需要安装 curl_cffi: pip install curl_cffi")

from .base import FetchStrategy, FetchResult

JINA_PREFIX = "https://r.jina.ai/"


class ProxyFetch(FetchStrategy):
    """Jina Reader 代理抓取，返回 Markdown 格式内容."""

    @property
    def name(self) -> str:
        return "proxy_fetch"

    def fetch(self, url: str, site_config: dict = None) -> FetchResult:
        jina_url = f"{JINA_PREFIX}{url}"
        headers = {"Accept": "text/markdown"}

        try:
            resp = cffi_requests.get(jina_url, headers=headers, timeout=45)
            content = resp.text
            ok = resp.status_code == 200 and len(content) > 100
            return FetchResult(html=content, status=resp.status_code, method=self.name, success=ok)
        except Exception as e:
            return FetchResult(html=str(e), status=0, method=self.name, success=False)
