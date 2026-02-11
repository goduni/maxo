from maxo.omit import Omittable, Omitted
from maxo.types.base import MaxoType
from maxo.types.chat_member import ChatMember


class ChatMembersList(MaxoType):
    """
    Args:
        marker: Указатель на следующую страницу данных
        members: Список участников чата с информацией о времени последней активности
    """

    members: list[ChatMember]

    marker: Omittable[int | None] = Omitted()
