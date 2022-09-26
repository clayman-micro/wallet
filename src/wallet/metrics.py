import time
from typing import Dict

import prometheus_client  # type: ignore
from aiohttp import web

from wallet.typing import Handler, Metric


async def handler(request: web.Request) -> web.Response:
    """Expose application metrics to the world."""
    resp = web.Response(body=prometheus_client.generate_latest(registry=request.app["metrics_registry"]))

    resp.content_type = prometheus_client.CONTENT_TYPE_LATEST
    return resp


@web.middleware
async def middleware(request: web.Request, handler: Handler) -> web.Response:
    """Middleware to collect http requests count and response latency."""
    start_time = time.monotonic()
    request.app["metrics"]["requests_in_progress"].labels(request.app["app_name"], request.path, request.method).inc()

    response = await handler(request)

    resp_time = time.monotonic() - start_time
    request.app["metrics"]["requests_latency"].labels(request.app["app_name"], request.path).observe(resp_time)
    request.app["metrics"]["requests_in_progress"].labels(request.app["app_name"], request.path, request.method).dec()
    request.app["metrics"]["requests_total"].labels(
        request.app["app_name"], request.method, request.path, response.status
    ).inc()

    return response


def setup(app: web.Application, extra_metrics: Dict[str, Metric] = None) -> None:
    """Connect metrics to application."""
    app["metrics_registry"] = prometheus_client.CollectorRegistry()
    app["metrics"] = {
        "requests_total": prometheus_client.Counter(
            "requests_total",
            "Total request count",
            ("app_name", "method", "endpoint", "http_status"),
            registry=app["metrics_registry"],
        ),
        "requests_latency": prometheus_client.Histogram(
            "requests_latency_seconds",
            "Request latency",
            ("app_name", "endpoint"),
            registry=app["metrics_registry"],
        ),
        "requests_in_progress": prometheus_client.Gauge(
            "requests_in_progress_total",
            "Requests in progress",
            ("app_name", "endpoint", "method"),
            registry=app["metrics_registry"],
        ),
    }

    if extra_metrics:
        for key, metric in extra_metrics.items():
            app["metrics"][key] = metric
            app["metrics_registry"].register(metric)

    app.middlewares.append(middleware)  # type: ignore

    app.router.add_get("/-/metrics", handler, name="metrics")
