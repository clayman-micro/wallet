import time
from types import TracebackType
from typing import Type

import prometheus_client

Metric = (
    prometheus_client.Counter
    | prometheus_client.Gauge
    | prometheus_client.Summary
    | prometheus_client.Histogram
    | prometheus_client.Info
    | prometheus_client.Enum
)

registry = prometheus_client.CollectorRegistry()


class Timer:
    """Timer context manager."""

    def __init__(self, metric: prometheus_client.Histogram) -> None:
        self.metric = metric

    def __enter__(self) -> None:
        """Start time calculation."""
        self.start_time = time.monotonic()

    def __exit__(
        self,
        exc_type: Type[BaseException] | None,
        exc: Exception | None,
        traceback: TracebackType | None,
    ) -> None:
        """End time calculation."""
        self.metric.observe(amount=time.monotonic() - self.start_time)


requests_total = prometheus_client.Counter(
    "requests_total",
    "Total request count",
    ("app_name", "version", "method", "endpoint", "http_status"),
    registry=registry,
)
request_latency = prometheus_client.Histogram(
    "requests_latency_seconds",
    "Request latency",
    ("app_name", "version", "endpoint", "method"),
    registry=registry,
)
requests_in_progress = prometheus_client.Gauge(
    "requests_in_progress_total",
    "Requests in progress",
    ("app_name", "version", "endpoint", "method"),
    registry=registry,
)
