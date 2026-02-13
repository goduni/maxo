from typing import Generic, TypeVar

from maxo.bot.bot import Bot
from maxo.routing.updates.base import BaseUpdate
from maxo.utils.facades.methods.bot import BotMethodsFacade

_UpdateT = TypeVar("_UpdateT", bound=BaseUpdate)


class BaseUpdateFacade(BotMethodsFacade, Generic[_UpdateT]):
    def __init__(
        self,
        bot: Bot,
        update: _UpdateT,
    ) -> None:
        super().__init__(bot)
        self._update = update

    @property
    def update(self) -> _UpdateT:
        return self._update
