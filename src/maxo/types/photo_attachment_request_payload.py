from maxo.omit import Omittable, Omitted
from maxo.types.base import MaxoType
from maxo.types.photo_token import PhotoToken


class PhotoAttachmentRequestPayload(MaxoType):
    """
    Запрос на прикрепление изображения (все поля являются взаимоисключающими)

    Args:
        photos: Токены, полученные после загрузки изображений
        token: Токен существующего вложения
        url: Любой внешний URL изображения, которое вы хотите прикрепить
    """

    photos: Omittable[list[PhotoToken] | None] = Omitted()  # TODO: Проверить кто это
    token: Omittable[str | None] = Omitted()
    url: Omittable[str | None] = Omitted()
