from maxo.routing.updates.dialog_cleared import DialogCleared
from maxo.types.user import User
from maxo.utils.facades.methods.chat import ChatMethodsFacade
from maxo.utils.facades.updates.base import BaseUpdateFacade


class DialogClearedFacade(
    BaseUpdateFacade[DialogCleared],
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
