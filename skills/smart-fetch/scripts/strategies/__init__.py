from .base import FetchStrategy, FetchResult
from .light_fetch import LightFetch
from .browser_fetch import BrowserFetch
from .proxy_fetch import ProxyFetch

__all__ = ["FetchStrategy", "FetchResult", "LightFetch", "BrowserFetch", "ProxyFetch"]
