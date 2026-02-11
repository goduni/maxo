from dataclasses import field
from typing import Self

from maxo.enums.attachment_type import AttachmentType
from maxo.omit import Omittable, Omitted
from maxo.types.attachment import Attachment
from maxo.types.share_attachment_payload import ShareAttachmentPayload


class ShareAttachment(Attachment):
    """
    Args:
        description: Описание предпросмотра ссылки
        image_url: Изображение предпросмотра ссылки
        payload:
        title: Заголовок предпросмотра ссылки.
        type:
    """

    type: AttachmentType = AttachmentType.SHARE

    payload: ShareAttachmentPayload = field(default_factory=ShareAttachmentPayload)

    description: Omittable[str | None] = Omitted()
    image_url: Omittable[str | None] = Omitted()
    title: Omittable[str | None] = Omitted()

    @classmethod
    def factory(
        cls,
        url: Omittable[str | None] = Omitted(),
        token: Omittable[str | None] = Omitted(),
        title: Omittable[str | None] = Omitted(),
        description: Omittable[str | None] = Omitted(),
        image_url: Omittable[str | None] = Omitted(),
    ) -> Self:
        return cls(
            payload=ShareAttachmentPayload(
                url=url,
                token=token,
            ),
            title=title,
            description=description,
            image_url=image_url,
        )
