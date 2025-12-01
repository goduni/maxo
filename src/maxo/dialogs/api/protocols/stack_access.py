from abc import abstractmethod
from typing import Protocol

from maxo import Ctx
from maxo.dialogs import ChatEvent
from maxo.dialogs.api.entities import Context, Stack


class StackAccessValidator(Protocol):
    @abstractmethod
    async def is_allowed(
        self,
        stack: Stack,
        context: Context | None,
        event: ChatEvent,
        ctx: Ctx,
    ) -> bool:
        """Check if current user is allowed to interactor with dialog."""
        raise NotImplementedError
