from maxo.types.base import MaxoType


class PhotoToken(MaxoType):
    """
    Args:
        token: Закодированная информация загруженного изображения
    """

    token: str
