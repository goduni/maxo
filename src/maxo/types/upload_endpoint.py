from maxo.omit import Omittable, Omitted
from maxo.types.base import MaxoType


class UploadEndpoint(MaxoType):
    """
    Точка доступа, куда следует загружать ваши бинарные файлы

    Args:
        token: Видео- или аудио-токен для отправки сообщения
        url: URL для загрузки файла
    """

    url: str

    token: Omittable[str] = Omitted()
