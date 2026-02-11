from maxo.omit import Omittable, Omitted
from maxo.types.base import MaxoType
from maxo.types.message import Message


class GetPinnedMessageResult(MaxoType):
    """
    Args:
        message: Закреплённое сообщение. Может быть `null`, если в чате нет закреплённого сообщения
    """

    message: Omittable[Message | None] = Omitted()
