from maxo.omit import Omittable, Omitted
from maxo.types.base import MaxoType


class ShareAttachmentPayload(MaxoType):
    """
    Полезная нагрузка запроса ShareAttachmentRequest

    Args:
        token: Токен вложения
        url: URL, прикрепленный к сообщению в качестве предпросмотра медиа
    """

    token: Omittable[str | None] = Omitted()
    url: Omittable[str | None] = Omitted()
