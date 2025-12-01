from abc import abstractmethod
from collections.abc import Callable
from typing import Any

from maxo.dialogs.api.entities import ChatEvent
from maxo.dialogs.api.protocols import DialogManager


class WidgetEventProcessor:
    @abstractmethod
    async def process_event(
        self,
        event: ChatEvent,
        source: Any,
        manager: DialogManager,
        *args,
        **kwargs,
    ):
        raise NotImplementedError


class SimpleEventProcessor(WidgetEventProcessor):
    def __init__(self, callback: Callable):
        self.callback = callback

    async def process_event(
        self,
        event: ChatEvent,
        source: Any,
        manager: DialogManager,
        *args,
        **kwargs,
    ):
        if self.callback:
            await self.callback(event, source, manager, *args, **kwargs)


def ensure_event_processor(
    processor: Callable | WidgetEventProcessor | None,
) -> WidgetEventProcessor:
    if isinstance(processor, WidgetEventProcessor):
        return processor
    return SimpleEventProcessor(processor)
