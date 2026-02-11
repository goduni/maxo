from maxo.enums import ButtonType
from maxo.types.base import MaxoType


class Button(MaxoType):
    """
    Args:
        text: Видимый текст кнопки
        type:
    """

    text: str
    type: ButtonType
