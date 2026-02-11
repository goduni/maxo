from maxo.omit import Omittable, Omitted
from maxo.types.user import User


class UserWithPhoto(User):
    """
    Объект с общей информацией о пользователе или боте, дополнительно содержит URL аватара и описание

    Args:
        avatar_url: URL аватара пользователя или бота в уменьшенном размере
        description: Описание пользователя или бота. В случае с пользователем может принимать значение `null`, если описание не заполнено
        full_avatar_url: URL аватара пользователя или бота в полном размере
    """

    avatar_url: Omittable[str] = Omitted()
    description: Omittable[str | None] = Omitted()
    full_avatar_url: Omittable[str] = Omitted()
