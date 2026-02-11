from maxo.omit import Omittable, Omitted
from maxo.types.base import MaxoType


class BotCommand(MaxoType):
    """
    до 32 элементов
    Команды, поддерживаемые ботом

    Args:
        description: Описание команды
        name: Название команды
    """

    name: str

    description: Omittable[str | None] = Omitted()
