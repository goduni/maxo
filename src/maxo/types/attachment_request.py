from maxo.enums.attachment_request_type import AttachmentRequestType
from maxo.types.base import MaxoType


class AttachmentRequest(MaxoType):
    """
    Запрос на прикрепление данных к сообщению

    Args:
        type:
    """

    type: AttachmentRequestType
