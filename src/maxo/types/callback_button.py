from maxo.enums.button_type import ButtonType
from maxo.types.button import Button


class CallbackButton(Button):
    """
    После нажатия на такую кнопку клиент отправляет на сервер полезную нагрузку, которая содержит

    Args:
        payload: Токен кнопки
        type:
    """

    type: ButtonType = ButtonType.CALLBACK

    payload: str
    """Токен кнопки"""

    # Подражание aiogram
    @property
    def callback_data(self) -> str:
        return self.payload
