from maxo.omit import Omittable, Omitted
from maxo.types.base import MaxoType


class SimpleQueryResult(MaxoType):
    """
    Простой ответ на запрос

    Args:
        message: Объяснительное сообщение, если результат не был успешным
        success: `true`, если запрос был успешным, `false` в противном случае
    """

    success: bool

    message: Omittable[str] = Omitted()
