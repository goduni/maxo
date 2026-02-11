from typing import Self

from maxo.enums.attachment_request_type import AttachmentRequestType
from maxo.omit import Omittable, Omitted
from maxo.types.attachment_request import AttachmentRequest
from maxo.types.photo_attachment_request_payload import PhotoAttachmentRequestPayload


class PhotoAttachmentRequest(AttachmentRequest):
    """
    Args:
        payload:
        type:
    """

    type: AttachmentRequestType = AttachmentRequestType.IMAGE

    payload: PhotoAttachmentRequestPayload

    @classmethod
    def factory(
        cls,
        *,
        url: Omittable[str | None] = Omitted(),
        token: Omittable[str | None] = Omitted(),
        photos: Omittable[list[str] | None] = Omitted(),
    ) -> Self:
        """
        Фабричный метод.

        Все поля являются взаимоисключающими.

        Args:
            url: Любой внешний URL изображения, которое вы хотите прикрепить. От 1 символа.
            token: Токен существующего вложения.
            photos: Токены, полученные после загрузки изображений

        """
        return cls(
            payload=PhotoAttachmentRequestPayload(
                url=url,
                token=token,
                photos=photos,
            ),
        )
