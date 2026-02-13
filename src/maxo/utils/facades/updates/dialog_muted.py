from datetime import datetime

from maxo.routing.updates.dialog_muted import DialogMuted
from maxo.types.user import User
from maxo.utils.facades.methods.chat import ChatMethodsFacade
from maxo.utils.facades.updates.base import BaseUpdateFacade


class DialogMutedFacade(
    BaseUpdateFacade[DialogMuted],
    ChatMethodsFacade,
):
    @property
    def chat_id(self) -> int:
        return self._update.chat_id

    @property
    def user(self) -> User:
        return self._update.user

    @property
    def muted_until(self) -> datetime:
        return self._update.muted_until

    @property
    def user_locale(self) -> str:
        return self._update.user_locale
