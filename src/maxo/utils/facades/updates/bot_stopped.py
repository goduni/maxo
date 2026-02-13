from maxo.omit import Omittable
from maxo.routing.updates.bot_stopped import BotStopped
from maxo.types.user import User
from maxo.utils.facades.methods.chat import ChatMethodsFacade
from maxo.utils.facades.updates.base import BaseUpdateFacade


class BotStoppedFacade(
    BaseUpdateFacade[BotStopped],
    ChatMethodsFacade,
):
    @property
    def chat_id(self) -> int:
        return self._update.chat_id

    @property
    def user(self) -> User:
        return self._update.user

    @property
    def user_locale(self) -> Omittable[str]:
        return self._update.user_locale
