from maxo import Ctx
from maxo.dialogs.api.entities import ChatEvent
from maxo.dialogs.api.internal import DataGetter, DialogManagerFactory
from maxo.dialogs.api.protocols import (
    DialogManager,
    DialogRegistryProtocol,
    MediaIdStorageProtocol,
    MessageManagerProtocol,
)
from maxo.routing.interfaces import BaseRouter

from .manager import ManagerImpl


class DefaultManagerFactory(DialogManagerFactory):
    def __init__(
        self,
        message_manager: MessageManagerProtocol,
        media_id_storage: MediaIdStorageProtocol,
        getter: DataGetter | None,
    ) -> None:
        self.message_manager = message_manager
        self.media_id_storage = media_id_storage
        self.getter = getter

    def __call__(
        self,
        event: ChatEvent,
        ctx: Ctx,
        registry: DialogRegistryProtocol,
        router: BaseRouter,
    ) -> DialogManager:
        return ManagerImpl(
            event=event,
            ctx=ctx,
            message_manager=self.message_manager,
            media_id_storage=self.media_id_storage,
            registry=registry,
            router=router,
            getter=self.getter,
        )
