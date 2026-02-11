from maxo.enums.button_type import ButtonType
from maxo.omit import Omittable, Omitted
from maxo.types.button import Button


class MessageButton(Button):
    """
    Кнопка для запуска мини-приложения

    Args:
        text: Текст кнопки, который будет отправлен в чат от лица пользователя
        type:
    """

    type: ButtonType = ButtonType.MESSAGE

    text: Omittable[str] = Omitted()
