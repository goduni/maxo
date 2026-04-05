from datetime import datetime

from maxo.enums.chat_admin_permission import ChatAdminPermission
from maxo.errors import AttributeIsEmptyError
from maxo.omit import Omittable, Omitted, is_defined
from maxo.types.user_with_photo import UserWithPhoto


class ChatMember(UserWithPhoto):
    """
    Объект включает общую информацию о пользователе или боте, URL аватара и описание (при наличии). Дополнительно содержит данные для пользователей-участников чата. Возвращается только при вызове некоторых методов группы `/chats`, например [`GET /chats/{chatId}/members`](https://dev.max.ru/docs-api/methods/GET/chats/-chatId-/members)

    Args:
        alias: Заголовок, который будет показан на клиенте
            Если пользователь администратор или владелец и ему не установлено это название, то поле не передаётся, клиенты на своей стороне подменят на "владелец" или "админ"
        is_admin: Является ли пользователь администратором чата
        is_owner: Является ли пользователь владельцем чата
        join_time: Дата присоединения к чату в формате Unix time
        last_access_time: Время последней активности пользователя в чате. Может быть устаревшим для суперчатов (равно времени вступления)
        permissions: Перечень прав пользователя. Возможные значения:
            - `"read_all_messages"` — Читать все сообщения.
            - `"add_remove_members"` — Добавлять/удалять участников.
            - `"add_admins"` — Добавлять администраторов.
            - `"change_chat_info"` — Изменять информацию о чате.
            - `"pin_message"` — Закреплять сообщения.
            - `"write"` — Писать сообщения.
            - `"edit_link"` — Изменять ссылку на чат.
    """

    is_admin: bool
    """Является ли пользователь администратором чата"""
    is_owner: bool
    """Является ли пользователь владельцем чата"""
    join_time: datetime
    """Дата присоединения к чату в формате Unix time"""
    last_access_time: datetime
    """Время последней активности пользователя в чате. Может быть устаревшим для суперчатов (равно времени вступления)"""

    permissions: list[ChatAdminPermission] | None = None
    """
    Перечень прав пользователя. Возможные значения:
        - `"read_all_messages"` — Читать все сообщения.
        - `"add_remove_members"` — Добавлять/удалять участников.
        - `"add_admins"` — Добавлять администраторов.
        - `"change_chat_info"` — Изменять информацию о чате.
        - `"pin_message"` — Закреплять сообщения.
        - `"write"` — Писать сообщения.
        - `"edit_link"` — Изменять ссылку на чат.
    """

    alias: Omittable[str] = Omitted()
    """
    Заголовок, который будет показан на клиенте

    Если пользователь администратор или владелец и ему не установлено это название, то поле не передаётся, клиенты на своей стороне подменят на "владелец" или "админ"
    """

    @property
    def unsafe_alias(self) -> str:
        if is_defined(self.alias):
            return self.alias

        raise AttributeIsEmptyError(
            obj=self,
            attr="alias",
        )

    @property
    def unsafe_permissions(self) -> list[ChatAdminPermission]:
        if is_defined(self.permissions):
            return self.permissions

        raise AttributeIsEmptyError(
            obj=self,
            attr="permissions",
        )
