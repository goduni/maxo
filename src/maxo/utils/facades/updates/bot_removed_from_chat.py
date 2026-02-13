from maxo.routing.updates.bot_removed_from_chat import BotRemovedFromChat
from maxo.types.user import User
from maxo.utils.facades.methods.chat import ChatMethodsFacade
from maxo.utils.facades.updates.base import BaseUpdateFacade


class BotRemovedFromChatFacade(
    BaseUpdateFacade[BotRemovedFromChat],
    ChatMethodsFacade,
):
    @property
    def chat_id(self) -> int:
        return self._update.chat_id

    @property
    def user(self) -> User:
        return self._update.user

    @property
    def is_channel(self) -> bool:
        return self._update.is_channel
