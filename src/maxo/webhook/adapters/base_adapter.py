from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping
from ipaddress import IPv4Address, IPv6Address
from typing import TYPE_CHECKING, Any, Generic, TypeVar

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from maxo.webhook.adapters.base_mapping import MappingABC

R = TypeVar("R")


class BoundRequest(ABC, Generic[R]):
    """Unified abstraction for requests across frameworks."""

    __slots__ = ("request",)

    def __init__(self, request: R) -> None:
        self.request = request

    @abstractmethod
    async def json(self) -> dict[str, Any]:
        """Get JSON data from request."""
        raise NotImplementedError

    @property
    @abstractmethod
    def client_ip(self) -> IPv4Address | IPv6Address | str | None:
        """Get client IP address."""
        raise NotImplementedError

    @property
    @abstractmethod
    def headers(self) -> MappingABC[Mapping[str, Any]]:
        """Get request headers."""
        raise NotImplementedError

    @property
    @abstractmethod
    def query_params(self) -> MappingABC[Mapping[str, Any]]:
        """Get request query parameters."""
        raise NotImplementedError

    @property
    @abstractmethod
    def path_params(self) -> dict[str, Any]:
        """Get request path parameters."""
        raise NotImplementedError


class WebAdapter(ABC):
    """Abstraction for web framework adapters."""

    @abstractmethod
    def bind(self, request: Any) -> BoundRequest:
        """Bind request to BoundRequest."""
        raise NotImplementedError

    @abstractmethod
    def register(
        self,
        app: Any,
        path: str,
        handler: Callable[[BoundRequest], Awaitable[Any]],
        on_startup: Callable[..., Awaitable[Any]] | None = None,
        on_shutdown: Callable[..., Awaitable[Any]] | None = None,
    ) -> None:
        """
        Register webhook handler.

        :param app: Web application instance.
        :param path: Webhook path.
        :param handler: Handler function.
        :param on_startup: Optional startup callback.
        :param on_shutdown: Optional shutdown callback.
        """
        raise NotImplementedError

    @abstractmethod
    def create_json_response(self, status: int, payload: dict[str, Any]) -> Any:
        """Create JSON response with given status and data."""
        raise NotImplementedError
