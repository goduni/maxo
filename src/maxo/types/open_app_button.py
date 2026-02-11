from maxo.enums.button_type import ButtonType
from maxo.omit import Omittable, Omitted
from maxo.types.button import Button


class OpenAppButton(Button):
    """
    Кнопка для запуска мини-приложения

    Args:
        contact_id: Идентификатор бота, чьё мини-приложение надо запустить
        payload: Параметр запуска, который будет передан в [initData](/docs/webapps/bridge#WebAppData) мини-приложения
        type:
        web_app: Публичное имя (username) бота или ссылка на него, чьё мини-приложение надо запустить
    """

    type: ButtonType = ButtonType.OPEN_APP

    contact_id: Omittable[int] = Omitted()
    payload: Omittable[str] = Omitted()
    web_app: Omittable[str] = Omitted()
