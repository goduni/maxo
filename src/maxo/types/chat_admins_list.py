from maxo.omit import Omittable, Omitted
from maxo.types.base import MaxoType
from maxo.types.chat_admin import ChatAdmin


class ChatAdminsList(MaxoType):
    """
    Args:
        admins: Список пользователей, которые получат права администратора чата
        marker: Указатель на следующую страницу данных
    """

    admins: list[ChatAdmin]

    marker: Omittable[int | None] = Omitted()
