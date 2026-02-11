from maxo.types.base import MaxoType
from maxo.types.buttons import InlineButtons


class Keyboard(MaxoType):
    """
    Клавиатура - это двумерный массив кнопок

    Args:
        buttons:
    """

    buttons: list[list[InlineButtons]]
