from collections.abc import Sequence
from datetime import datetime

from maxo.enums.chat_admin_permission import ChatAdminPermission
from maxo.omit import Omittable, Omitted
from maxo.types.user_with_photo import UserWithPhoto


class ChatMembership(UserWithPhoto):
    """
    Информация о членстве в чате.

    Args:
        is_owner: Является ли пользователь владельцем чата.
        is_admin: Является ли пользователь администратором чата
        join_time: Дата присоединения к чату в формате Unix time
        permissions: Перечень прав пользователя.
        alias: Заголовок, который будет показан на клиенте.

    """

    is_owner: bool
    is_admin: bool
    join_time: datetime
    permissions: Sequence[ChatAdminPermission]
    alias: Omittable[str] = Omitted()
