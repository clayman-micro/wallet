from typing import Awaitable, Callable

from aiohttp import web
from prometheus_client import Counter, Enum, Gauge, Histogram, Info, Summary  # type: ignore

Handler = Callable[[web.Request], Awaitable[web.Response]]

Metric = Counter | Gauge | Summary | Histogram | Info | Enum
