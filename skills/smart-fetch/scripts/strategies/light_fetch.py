"""Level 1: 轻量请求策略，使用 curl_cffi 模拟浏览器指纹."""
try:
    from curl_cffi import requests as cffi_requests
except ImportError:
    raise ImportError("需要安装 curl_cffi: pip install curl_cffi")

from .base import FetchStrategy, FetchResult

HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Sec-Ch-Ua": '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
}


class LightFetch(FetchStrategy):
    """curl_cffi 轻量抓取，带浏览器指纹模拟."""

    @property
    def name(self) -> str:
        return "light_fetch"

    def fetch(self, url: str, site_config: dict = None) -> FetchResult:
        headers = {**HEADERS}
        if site_config and site_config.get("extra_headers"):
            headers.update(site_config["extra_headers"])

        try:
            resp = cffi_requests.get(
                url, headers=headers, impersonate="chrome", timeout=15
            )
            html = resp.text
            ok = resp.status_code == 200 and len(html) > 1000
            return FetchResult(html=html, status=resp.status_code, method=self.name, success=ok)
        except Exception as e:
            return FetchResult(html=str(e), status=0, method=self.name, success=False)
