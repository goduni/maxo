from maxo.types.base import MaxoType
from maxo.types.message import Message


class MessageList(MaxoType):
    """
    Пагинированный список сообщений

    Args:
        messages: Массив сообщений
    """

    messages: list[Message]
