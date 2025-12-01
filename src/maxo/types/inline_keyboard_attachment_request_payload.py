from collections.abc import Sequence

from maxo.types.base import MaxoType
from maxo.types.keyboard_buttons import KeyboardButtons


class InlineKeyboardAttachmentRequestPayload(MaxoType):
    """
    Полезная нагрузка для запроса на прикрепление inline клавиатуры.

    Args:
        buttons: Двумерный массив кнопок. От 1 элемента

    """

    buttons: Sequence[Sequence[KeyboardButtons]]
