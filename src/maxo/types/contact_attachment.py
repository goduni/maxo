from typing import Self

from maxo.enums.attachment_type import AttachmentType
from maxo.omit import Omittable, Omitted
from maxo.types.attachment import Attachment
from maxo.types.contact_attachment_payload import ContactAttachmentPayload
from maxo.types.user import User


class ContactAttachment(Attachment):
    """
    Args:
        payload:
        type:
    """

    type: AttachmentType = AttachmentType.CONTACT

    payload: ContactAttachmentPayload

    @classmethod
    def factory(
        cls,
        vcf_info: Omittable[str | None] = Omitted(),
        max_info: Omittable[User | None] = Omitted(),
    ) -> Self:
        """
        Фабричный метод.

        Args:
            vcf_info: Информация о пользователе в формате VCF.
            max_info: Информация о пользователе.

        """
        return cls(
            payload=ContactAttachmentPayload(
                max_info=max_info,
                vcf_info=vcf_info,
            ),
        )
