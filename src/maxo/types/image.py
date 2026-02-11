from maxo.types.base import MaxoType


class Image(MaxoType):
    """
    Общая схема, описывающая объект изображения

    Args:
        url: URL изображения
    """

    url: str
