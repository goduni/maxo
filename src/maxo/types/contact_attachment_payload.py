from maxo.omit import Omittable, Omitted
from maxo.types.base import MaxoType
from maxo.types.user import User


class ContactAttachmentPayload(MaxoType):
    """
    Args:
        max_info: Информация о пользователе
        vcf_info: Информация о пользователе в формате VCF.
    """

    max_info: Omittable[User | None] = Omitted()
    vcf_info: Omittable[str | None] = Omitted()
