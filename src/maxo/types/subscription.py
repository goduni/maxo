from datetime import datetime

from maxo.types.base import MaxoType


class Subscription(MaxoType):
    """
    Схема для описания подписки на WebHook

    Args:
        time: Unix-время, когда была создана подписка
        update_types: Типы обновлений, на которые подписан бот
        url: URL вебхука
    """

    time: datetime
    url: str

    update_types: list[str] | None = None
