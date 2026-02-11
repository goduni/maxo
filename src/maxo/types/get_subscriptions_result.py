from maxo.types.base import MaxoType
from maxo.types.subscription import Subscription


class GetSubscriptionsResult(MaxoType):
    """
    Список всех WebHook подписок

    Args:
        subscriptions: Список текущих подписок
    """

    subscriptions: list[Subscription]
