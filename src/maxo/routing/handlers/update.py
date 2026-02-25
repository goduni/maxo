import asyncio
import inspect
from functools import partial
from typing import Any, Generic, Protocol, TypeVar, runtime_checkable

from maxo.routing.ctx import Ctx
from maxo.routing.filters.always import AlwaysTrueFilter
from maxo.routing.interfaces.filter import Filter
from maxo.routing.interfaces.handler import Handler
from maxo.routing.updates.base import BaseUpdate

_UpdateT = TypeVar("_UpdateT", bound=BaseUpdate)
_ReturnT_co = TypeVar("_ReturnT_co", covariant=True)


@runtime_checkable
class UpdateHandlerFn(Protocol[_UpdateT, _ReturnT_co]):
    async def __call__(
        self,
        update: _UpdateT,
        /,
        *args: Any,
        **kwargs: Any,
    ) -> _ReturnT_co: ...


class UpdateHandler(
    Handler[_UpdateT, _ReturnT_co],
    Generic[_UpdateT, _ReturnT_co],
):
    __slots__ = (
        "_awaitable",
        "_filter",
        "_handler_fn",
        "_params",
        "_varkw",
    )

    def __init__(
        self,
        handler_fn: UpdateHandlerFn[_UpdateT, _ReturnT_co],
        filter: Filter[_UpdateT] | None = None,
    ) -> None:
        if filter is None:
            filter = AlwaysTrueFilter()

        self._filter = filter
        self._handler_fn = handler_fn
        self._awaitable = inspect.isawaitable(
            handler_fn,
        ) or inspect.iscoroutinefunction(handler_fn)
        spec = inspect.getfullargspec(handler_fn)
        self._params = {*spec.args, *spec.kwonlyargs}
        self._varkw = spec.varkw is not None

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}"
            f"(handler_fn={self._handler_fn}, filter={self._filter})"
        )

    def _prepare_kwargs(self, ctx: Ctx) -> dict[str, Any]:
        if self._varkw:
            return ctx

        return {k: ctx[k] for k in self._params if k in ctx}

    async def execute_filter(self, ctx: Ctx) -> bool:
        return await self._filter(ctx["update"], ctx)

    async def __call__(self, ctx: Ctx) -> _ReturnT_co:
        update = ctx.pop("update")
        wrapped = partial(self._handler_fn, update, **self._prepare_kwargs(ctx))
        try:
            if self._awaitable:
                return await wrapped()
            return await asyncio.to_thread(wrapped)
        finally:
            ctx["update"] = update
