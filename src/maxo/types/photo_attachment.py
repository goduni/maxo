from typing import Self

from maxo.enums.attachment_type import AttachmentType
from maxo.types.attachment import Attachment
from maxo.types.photo_attachment_payload import PhotoAttachmentPayload
from maxo.types.photo_attachment_request import PhotoAttachmentRequest


class PhotoAttachment(Attachment):
    """
    Вложение изображения

    Args:
        payload:
        type:
    """

    type: AttachmentType = AttachmentType.IMAGE

    payload: PhotoAttachmentPayload

    @classmethod
    def factory(
        cls,
        photo_id: int,
        token: str,
        url: str,
    ) -> Self:
        """
        Фабричный метод.

        Args:
            photo_id: Уникальный ID этого изображения
            token: Используйте token, если вы пытаетесь повторно использовать одно и то же вложение в другом сообщении.
            url: URL изображения

        """
        return cls(
            payload=PhotoAttachmentPayload(
                photo_id=photo_id,
                token=token,
                url=url,
            ),
        )

    def to_request(self) -> PhotoAttachmentRequest:
        return PhotoAttachmentRequest.factory(token=self.payload.token)
