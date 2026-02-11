from maxo.enums.message_link_type import MessageLinkType
from maxo.types.base import MaxoType


class NewMessageLink(MaxoType):
    """
    Args:
        mid: ID сообщения исходного сообщения
        type: Тип ссылки сообщения
    """

    mid: str
    type: MessageLinkType
