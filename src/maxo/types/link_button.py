from maxo.enums.button_type import ButtonType
from maxo.types.button import Button


class LinkButton(Button):
    """
    После нажатия на такую кнопку пользователь переходит по ссылке, которую она содержит

    Args:
        type:
        url:
    """

    type: ButtonType = ButtonType.LINK

    url: str
