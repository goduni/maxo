from maxo.routing.updates.chat_title_changed import ChatTitleChanged
from maxo.types.user import User
from maxo.utils.facades.methods.chat import ChatMethodsFacade
from maxo.utils.facades.updates.base import BaseUpdateFacade


class ChatTitleChangedFacade(
    BaseUpdateFacade[ChatTitleChanged],
    ChatMethodsFacade,
):
    @property
    def chat_id(self) -> int:
        return self._update.chat_id

    @property
    def user(self) -> User:
        return self._update.user

    @property
    def title(self) -> str:
        return self._update.title
