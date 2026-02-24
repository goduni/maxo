from abc import abstractmethod
from typing import TYPE_CHECKING

from maxo.enums.attachment_type import AttachmentType
from maxo.types.base import MaxoType

if TYPE_CHECKING:
    from maxo.types.attachments import AttachmentsRequests


class Attachment(MaxoType):
    """
    Общая схема, представляющая вложение сообщения

    Args:
        type:
    """

    type: AttachmentType

    @abstractmethod
    def to_request(self) -> "AttachmentsRequests":
        raise NotImplementedError
