from typing import Any, Dict, List, Optional, Tuple

from aiohttp import web
from aiohttp_micro.web.handlers import openapi
from apispec import APISpec  # type: ignore
from apispec.ext.marshmallow import MarshmallowPlugin  # type: ignore


def setup(
    app: web.Application,
    *,
    title: str,
    version: str,
    description: str,
    operations: List[Any],
    openapi_version: str = "3.0.2",
    path: str = "/api/spec.json",
    security: Optional[Tuple[str, Dict[str, str]]] = None,
) -> None:

    app["spec"] = APISpec(
        title=title,
        version=version,
        openapi_version=openapi_version,
        info={"description": description},
        plugins=[MarshmallowPlugin()],
    )

    if security:
        app["spec"].components.security_scheme(*security)

    app.router.add_get(path, openapi.handler, name="api.spec")

    for method, path, view in operations:
        app.router.add_route(method, path, view.handle)

        operation = view.spec.generate()
        operation.setdefault("description", view.__doc__)

        app["spec"].path(
            path=path, operations={method.lower(): operation},
        )
