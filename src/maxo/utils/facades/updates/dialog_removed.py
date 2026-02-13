from maxo.routing.updates.dialog_removed import DialogRemoved
from maxo.types.user import User
from maxo.utils.facades.methods.chat import ChatMethodsFacade
from maxo.utils.facades.updates.base import BaseUpdateFacade


class DialogRemovedFacade(
    BaseUpdateFacade[DialogRemoved],
    ChatMethodsFacade,
):
    @property
    def chat_id(self) -> int:
        return self._update.chat_id

    @property
    def user(self) -> User:
        return self._update.user

    @property
    def user_locale(self) -> str:
        return self._update.user_locale
