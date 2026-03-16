from collections.abc import Awaitable, Callable
from ipaddress import IPv4Address, IPv6Address
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from maxo.webhook.adapters.base_adapter import BoundRequest, WebAdapter
from maxo.webhook.adapters.fastapi.mapping import (
    FastAPIHeadersMapping,
    FastAPIQueryMapping,
)


class FastAPIBoundRequest(BoundRequest[Request]):
    def __init__(self, request: Request) -> None:
        super().__init__(request)
        self._headers = FastAPIHeadersMapping(self.request.headers)
        self._query_params = FastAPIQueryMapping(self.request.query_params)

    async def json(self) -> dict[str, Any]:
        return await self.request.json()

    @property
    def client_ip(self) -> IPv4Address | IPv6Address | str | None:
        if self.request.client:
            return self.request.client.host
        return None

    @property
    def headers(self) -> FastAPIHeadersMapping:
        return self._headers

    @property
    def query_params(self) -> FastAPIQueryMapping:
        return self._query_params

    @property
    def path_params(self) -> dict[str, Any]:
        return self.request.path_params


class FastApiWebAdapter(WebAdapter):
    def bind(self, request: Request) -> FastAPIBoundRequest:
        return FastAPIBoundRequest(request=request)

    def register(
        self,
        app: FastAPI,
        path: str,
        handler: Callable[[BoundRequest], Awaitable[Any]],
        on_startup: Callable[..., Awaitable[Any]] | None = None,
        on_shutdown: Callable[..., Awaitable[Any]] | None = None,
    ) -> None:
        async def endpoint(request: Request) -> Any:
            return await handler(self.bind(request))

        app.add_api_route(path=path, endpoint=endpoint, methods=["POST"])

        if on_startup is not None:
            app.add_event_handler("startup", on_startup)
        if on_shutdown is not None:
            app.add_event_handler("shutdown", on_shutdown)

    def create_json_response(
        self,
        status: int,
        payload: dict[str, Any],
    ) -> JSONResponse:
        return JSONResponse(status_code=status, content=payload)
