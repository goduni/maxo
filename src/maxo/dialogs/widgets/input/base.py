from abc import abstractmethod
from collections.abc import Awaitable, Callable, Sequence
from typing import Any

from magic_filter import F

from maxo.dialogs.api.internal import InputWidget
from maxo.dialogs.api.protocols import (
    DialogManager,
    DialogProtocol,
)
from maxo.dialogs.tools.filter_object import FilterObject
from maxo.dialogs.widgets.common import Actionable
from maxo.dialogs.widgets.widget_event import (
    WidgetEventProcessor,
    ensure_event_processor,
)
from maxo.enums import AttachmentType
from maxo.integrations.magic_filter import MagicFilter
from maxo.routing.updates import MessageCreated
from maxo.types import Message

MessageHandlerFunc = Callable[
    [Message, "MessageInput", DialogManager],
    Awaitable,
]


class BaseInput(Actionable, InputWidget):
    @abstractmethod
    async def process_message(
        self,
        message: MessageCreated,
        dialog: DialogProtocol,
        manager: DialogManager,
    ) -> bool:
        raise NotImplementedError


class MessageInput(BaseInput):
    def __init__(
        self,
        func: MessageHandlerFunc | WidgetEventProcessor | None,
        content_types: Sequence[str] | str = AttachmentType.ANY,
        filter: Callable[..., Any] | None = None,
        id: str | None = None,
    ):
        super().__init__(id=id)
        self.func = ensure_event_processor(func)

        # TODO: Починить
        filters = []
        if isinstance(content_types, str):
            if content_types != AttachmentType.ANY:
                filters.append(
                    FilterObject(MagicFilter(F.content_type == content_types)),
                )
        elif AttachmentType.ANY not in content_types:
            filters.append(FilterObject(MagicFilter(F.content_type.in_(content_types))))
        if filter is not None:
            filters.append(FilterObject(filter))
        self.filters = filters

    async def process_message(
        self,
        message: MessageCreated,
        dialog: DialogProtocol,
        manager: DialogManager,
    ) -> bool:
        for handler_filter in self.filters:
            if not await handler_filter.call(
                manager.event,
                **manager.middleware_data,
            ):
                return False
        await self.func.process_event(message, self, manager)
        return True
