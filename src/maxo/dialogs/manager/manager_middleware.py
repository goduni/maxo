from typing import Any

from maxo.dialogs.api.internal import STORAGE_KEY, DialogManagerFactory
from maxo.dialogs.api.protocols import (
    BgManagerFactory,
    DialogManager,
    DialogRegistryProtocol,
)
from maxo.routing.ctx import Ctx
from maxo.routing.interfaces import BaseMiddleware, BaseRouter, NextMiddleware
from maxo.routing.updates.base import MaxUpdate

MANAGER_KEY = "dialog_manager"
BG_FACTORY_KEY = "dialog_bg_factory"


class ManagerMiddleware(BaseMiddleware[MaxUpdate]):
    def __init__(
        self,
        dialog_manager_factory: DialogManagerFactory,
        registry: DialogRegistryProtocol,
        router: BaseRouter,
    ) -> None:
        super().__init__()
        self.dialog_manager_factory = dialog_manager_factory
        self.registry = registry
        self.router = router

    async def __call__(
        self,
        update: MaxUpdate,
        ctx: Ctx,
        next: NextMiddleware[MaxUpdate],
    ) -> Any:
        if self._is_event_supported(ctx):
            dialog_manager = self.dialog_manager_factory(
                event=update,
                ctx=ctx,
                registry=self.registry,
                router=self.router,
            )
            ctx[MANAGER_KEY] = dialog_manager

        try:
            return await next(ctx)
        finally:
            manager: DialogManager | None = ctx.get(MANAGER_KEY)
            if manager:
                await manager.close_manager()

    def _is_event_supported(
        self,
        ctx: Ctx,
    ) -> bool:
        return STORAGE_KEY in ctx


class BgFactoryMiddleware(BaseMiddleware[MaxUpdate]):
    def __init__(
        self,
        bg_manager_factory: BgManagerFactory,
    ) -> None:
        super().__init__()
        self.bg_manager_factory = bg_manager_factory

    async def __call__(
        self,
        update: MaxUpdate,
        ctx: Ctx,
        next: NextMiddleware[MaxUpdate],
    ) -> Any:
        ctx[BG_FACTORY_KEY] = self.bg_manager_factory
        return await next(ctx)
