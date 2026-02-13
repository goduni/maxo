from maxo.routing.updates.bot_added_to_chat import BotAddedToChat
from maxo.types.user import User
from maxo.utils.facades.methods.chat import ChatMethodsFacade
from maxo.utils.facades.updates.base import BaseUpdateFacade


class BotAddedToChatFacade(
    BaseUpdateFacade[BotAddedToChat],
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
