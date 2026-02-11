from typing import Self

from maxo.enums.attachment_type import AttachmentType
from maxo.omit import Omittable, Omitted, is_not_omitted
from maxo.types.attachment import Attachment
from maxo.types.media_attachment_payload import MediaAttachmentPayload
from maxo.types.video_thumbnail import VideoThumbnail


class VideoAttachment(Attachment):
    """
    Args:
        duration: Длина видео в секундах
        height: Высота видео
        payload:
        thumbnail: Миниатюра видео
        type:
        width: Ширина видео
    """

    type: AttachmentType = AttachmentType.VIDEO

    payload: MediaAttachmentPayload

    duration: Omittable[int | None] = Omitted()
    height: Omittable[int | None] = Omitted()
    thumbnail: Omittable[VideoThumbnail | None] = Omitted()
    width: Omittable[int | None] = Omitted()

    @classmethod
    def factory(
        cls,
        url: str,
        token: str,
        thumbnail_url: Omittable[str] = Omitted(),
        width: Omittable[int | None] = Omitted(),
        height: Omittable[int | None] = Omitted(),
        duration: Omittable[int | None] = Omitted(),
    ) -> Self:
        """
        Фабричный метод.

        Args:
            url: URL медиа-вложения. Для видео-вложения используйте метод GetVideoAttachmentDetails, чтобы получить прямые ссылки.
            token: Используйте token, если вы пытаетесь повторно использовать одно и то же вложение в другом сообщении..
            thumbnail_url: URL изображения
            width: Ширина видео
            height: Высота видео
            duration: Длина видео в секундах

        """
        thumbnail: Omittable[VideoThumbnail]

        if is_not_omitted(thumbnail_url):
            thumbnail = VideoThumbnail(url=thumbnail_url)
        else:
            thumbnail = Omitted()

        return cls(
            payload=MediaAttachmentPayload(
                url=url,
                token=token,
            ),
            thumbnail=thumbnail,
            width=width,
            height=height,
            duration=duration,
        )
