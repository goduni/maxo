from abc import abstractmethod
from typing import Any, Protocol

from maxo.dialogs.api.entities import Data, NewMessage
from maxo.dialogs.api.protocols import DialogProtocol
from maxo.fsm import State
from maxo.routing.updates import MessageCallback, MessageCreated

from .manager import DialogManager
from .widgets import Widget


class WindowProtocol(Protocol):
    @abstractmethod
    async def process_message(
        self,
        message: MessageCreated,
        dialog: "DialogProtocol",
        manager: DialogManager,
    ) -> bool:
        """Return True if message in handled."""
        raise NotImplementedError

    @abstractmethod
    async def process_callback(
        self,
        callback: MessageCallback,
        dialog: "DialogProtocol",
        manager: DialogManager,
    ) -> bool:
        """Return True if callback in handled."""
        raise NotImplementedError

    @abstractmethod
    async def process_result(
        self,
        start_data: Data,
        result: Any,
        manager: "DialogManager",
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    async def render(
        self,
        dialog: "DialogProtocol",
        manager: DialogManager,
    ) -> NewMessage:
        raise NotImplementedError

    @abstractmethod
    def get_state(self) -> State:
        raise NotImplementedError

    @abstractmethod
    def find(self, widget_id: str) -> Widget | None:
        raise NotImplementedError
