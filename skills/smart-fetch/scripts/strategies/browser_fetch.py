"""Level 2: 浏览器渲染策略，使用 DrissionPage 绕过反爬."""
import time

try:
    from DrissionPage import ChromiumPage, ChromiumOptions
except ImportError:
    raise ImportError("需要安装 DrissionPage: pip install DrissionPage")

from .base import FetchStrategy, FetchResult


class BrowserFetch(FetchStrategy):
    """DrissionPage 浏览器渲染抓取，可绕过知乎/微信等站点的403."""

    @property
    def name(self) -> str:
        return "browser_fetch"

    def fetch(self, url: str, site_config: dict = None) -> FetchResult:
        co = ChromiumOptions()
        co.set_argument('--headless=new')
        co.set_argument('--no-sandbox')
        co.set_argument('--disable-blink-features=AutomationControlled')
        co.set_argument('--window-size=1920,1080')
        co.set_argument('--lang=zh-CN')
        co.set_user_agent(
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/124.0.0.0 Safari/537.36'
        )

        page = None
        try:
            page = ChromiumPage(co)
            page.get(url)

            # 等待页面加载
            wait_sel = site_config.get("wait_selector") if site_config else None
            if wait_sel:
                page.ele(wait_sel, timeout=8)
            else:
                time.sleep(5)

            html = page.html
            ok = len(html) > 1000
            return FetchResult(html=html, status=200, method=self.name, success=ok)
        except Exception as e:
            return FetchResult(html=str(e), status=0, method=self.name, success=False)
        finally:
            if page:
                page.quit()
