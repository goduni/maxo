from typing import Self

from maxo.enums.attachment_request_type import AttachmentRequestType
from maxo.types.attachment_request import AttachmentRequest
from maxo.types.buttons import InlineButtons
from maxo.types.inline_keyboard_attachment_request_payload import (
    InlineKeyboardAttachmentRequestPayload,
)


class InlineKeyboardAttachmentRequest(AttachmentRequest):
    """
    Запрос на прикрепление клавиатуры к сообщению

    Args:
        payload:
        type:
    """

    type: AttachmentRequestType = AttachmentRequestType.INLINE_KEYBOARD

    payload: InlineKeyboardAttachmentRequestPayload

    @classmethod
    def factory(
        cls,
        buttons: list[list[InlineButtons]],
    ) -> Self:
        return cls(
            payload=InlineKeyboardAttachmentRequestPayload(
                buttons=buttons,
            ),
        )
