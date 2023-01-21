from typing import Awaitable, Callable

from aiohttp import web
from prometheus_client import Counter, Enum, Gauge, Histogram, Info, Summary

Handler = Callable[[web.Request], Awaitable[web.StreamResponse]]

Metric = Counter | Gauge | Summary | Histogram | Info | Enum
