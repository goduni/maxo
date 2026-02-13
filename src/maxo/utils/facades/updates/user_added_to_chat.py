from maxo.omit import Omittable
from maxo.routing.updates.user_added_to_chat import UserAddedToChat
from maxo.types.user import User
from maxo.utils.facades.methods.chat import ChatMethodsFacade
from maxo.utils.facades.updates.base import BaseUpdateFacade


class UserAddedToChatFacade(
    BaseUpdateFacade[UserAddedToChat],
    ChatMethodsFacade,
):
    @property
    def chat_id(self) -> int:
        return self._update.chat_id

    @property
    def user(self) -> User:
        return self._update.user

    @property
    def inviter_id(self) -> Omittable[int | None]:
        return self._update.inviter_id

    @property
    def is_channel(self) -> bool:
        return self._update.is_channel
