from collections.abc import Sequence

from maxo.types.base import MaxoType
from maxo.types.keyboard_buttons import KeyboardButtons


class Keyboard(MaxoType):
    """
    Клавиатура.

    Args:
        buttons: Двумерный массив кнопок.

    """

    buttons: Sequence[Sequence[KeyboardButtons]]
