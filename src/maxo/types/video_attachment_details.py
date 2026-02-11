from maxo.omit import Omittable, Omitted
from maxo.types.base import MaxoType
from maxo.types.photo_attachment_payload import PhotoAttachmentPayload
from maxo.types.video_urls import VideoUrls


class VideoAttachmentDetails(MaxoType):
    """
    Args:
        duration: Длина видео в секундах
        height: Высота видео
        thumbnail: Миниатюра видео
        token: Токен видео-вложения
        urls: URL-ы для скачивания или воспроизведения видео. Может быть null, если видео недоступно
        width: Ширина видео
    """

    duration: int
    height: int
    token: str
    width: int

    thumbnail: Omittable[PhotoAttachmentPayload | None] = Omitted()
    urls: Omittable[VideoUrls | None] = Omitted()
