from maxo.enums.update_type import UpdateType
from maxo.errors import AttributeIsEmptyError
from maxo.omit import Omittable, Omitted, is_defined
from maxo.routing.updates.base import MaxUpdate
from maxo.types.user import User


class DialogUnmuted(MaxUpdate):
    """
    Вы получите этот update, когда пользователь включит уведомления в диалоге с ботом

    Args:
        chat_id: ID чата, где произошло событие
        type:
        user: Пользователь, который включил уведомления
        user_locale: Текущий язык пользователя в формате IETF BCP 47
    """

    type = UpdateType.DIALOG_UNMUTED

    chat_id: int
    """ID чата, где произошло событие"""
    user: User
    """Пользователь, который включил уведомления"""

    user_locale: Omittable[str] = Omitted()
    """Текущий язык пользователя в формате IETF BCP 47"""

    @property
    def unsafe_user_locale(self) -> str:
        if is_defined(self.user_locale):
            return self.user_locale

        raise AttributeIsEmptyError(
            obj=self,
            attr="user_locale",
        )
