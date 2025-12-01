from collections.abc import Sequence
from typing import Self

from maxo.types.base import MaxoType
from maxo.types.inline_keyboard_attachment_request_payload import (
    InlineKeyboardAttachmentRequestPayload,
)
from maxo.types.keyboard_buttons import KeyboardButtons


class InlineKeyboardAttachmentRequest(MaxoType):
    """
    Запрос на прикрепление inline клавиатуры.

    Args:
        payload: Полезная нагрузка для запроса на прикрепление inline клавиатуры.

    """

    payload: InlineKeyboardAttachmentRequestPayload

    @classmethod
    def factory(
        cls,
        buttons: Sequence[Sequence[KeyboardButtons]],
    ) -> Self:
        return cls(
            payload=InlineKeyboardAttachmentRequestPayload(
                buttons=buttons,
            ),
        )
