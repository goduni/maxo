from typing import Self

from maxo.enums.attachment_type import AttachmentType
from maxo.types.attachment import Attachment
from maxo.types.file_attachment_payload import FileAttachmentPayload


class FileAttachment(Attachment):
    """
    Args:
        filename: Имя загруженного файла
        payload:
        size: Размер файла в байтах
        type:
    """

    type: AttachmentType = AttachmentType.FILE

    filename: str
    payload: FileAttachmentPayload
    size: int

    @classmethod
    def factory(
        cls,
        url: str,
        token: str,
        filename: str,
        size: int,
    ) -> Self:
        """
        Фабричный метод.

        Args:
            url: URL медиа-вложения. Для видео-вложения используйте метод `GetVideoAttachmentDetails`, чтобы получить прямые ссылки.
            token: Используйте token, если вы пытаетесь повторно использовать одно и то же вложение в другом сообщении.
            filename: Имя загруженного файла
            size: Размер файла в байтах

        """
        return cls(
            payload=FileAttachmentPayload(
                url=url,
                token=token,
            ),
            filename=filename,
            size=size,
        )
