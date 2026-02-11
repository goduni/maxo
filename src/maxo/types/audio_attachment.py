from typing import Self

from maxo.enums.attachment_type import AttachmentType
from maxo.omit import Omittable, Omitted
from maxo.types.attachment import Attachment
from maxo.types.media_attachment_payload import MediaAttachmentPayload


class AudioAttachment(Attachment):
    """
    Args:
        payload:
        transcription: Аудио транскрипция
        type:
    """

    type: AttachmentType = AttachmentType.AUDIO

    payload: MediaAttachmentPayload

    transcription: Omittable[str | None] = Omitted()

    @classmethod
    def factory(
        cls,
        url: str,
        token: str,
        transcription: Omittable[str | None] = Omitted(),
    ) -> Self:
        """
        Фабричный метод.

        Args:
            url: URL медиа-вложения. Для видео-вложения используйте метод GetVideoAttachmentDetails, чтобы получить прямые ссылки.
            token: Используйте token, если вы пытаетесь повторно использовать одно и то же вложение в другом сообщении.
            transcription: Транскрипция аудио.

        """
        return cls(
            payload=MediaAttachmentPayload(
                url=url,
                token=token,
            ),
            transcription=transcription,
        )
