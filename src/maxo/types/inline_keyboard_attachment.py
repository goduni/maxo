from typing import Self

from maxo.enums.attachment_type import AttachmentType
from maxo.types.attachment import Attachment
from maxo.types.buttons import InlineButtons
from maxo.types.keyboard import Keyboard


class InlineKeyboardAttachment(Attachment):
    """
    Кнопки в сообщении

    Args:
        payload:
        type:
    """

    type: AttachmentType = AttachmentType.INLINE_KEYBOARD

    payload: Keyboard

    @classmethod
    def factory(cls, buttons: list[list[InlineButtons]]) -> Self:
        """
        Фабричный метод.

        Args:
            buttons: Двумерный массив кнопок.

        """
        return cls(
            payload=Keyboard(
                buttons=buttons,
            ),
        )
