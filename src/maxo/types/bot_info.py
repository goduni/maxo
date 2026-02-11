from maxo.omit import Omittable, Omitted
from maxo.types.bot_command import BotCommand
from maxo.types.user_with_photo import UserWithPhoto


class BotInfo(UserWithPhoto):
    """
    Объект включает общую информацию о боте, URL аватара и описание. Дополнительно содержит список команд, поддерживаемых ботом. Возвращается только при вызове метода `GET /me`

    Args:
        commands: Команды, поддерживаемые ботом
    """

    commands: Omittable[list[BotCommand] | None] = Omitted()
