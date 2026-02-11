from maxo.enums.chat_admin_permission import ChatAdminPermission
from maxo.omit import Omittable, Omitted
from maxo.types.base import MaxoType


class ChatAdmin(MaxoType):
    """
    Args:
        alias: Заголовок, который будет показан на клиенте
            Если пользователь администратор или владелец и ему не установлено это название, то поле не передаётся, клиенты на своей стороне подменят на "владелец" или "админ"
        permissions: Перечень прав доступа пользователя. Возможные значения:
            - `"read_all_messages"` — Читать все сообщения. Это право важно при назначении ботов: без него бот не будет получать апдейты (вебхуки) в групповом чате
            - `"add_remove_members"` — Добавлять/удалять участников
            - `"add_admins"` — Добавлять администраторов
            - `"change_chat_info"` — Изменять информацию о чате
            - `"pin_message"` — Закреплять сообщения
            - `"write"` — Писать сообщения
            - `"can_call"` — Совершать звонки
            - `"edit_link"` — Изменять ссылку на чат
            - `"post_edit_delete_message"` — Публиковать, редактировать и удалять сообщения
            - `"edit_message"` — Редактировать сообщения
            - `"delete_message"` — Удалять сообщения
            Если право назначается администратору, то обновляются его текущие права доступа
        user_id: Идентификатор пользователя-участника чата, который назначается администратором
            Максимум — 50 администраторов в чате
    """

    permissions: list[ChatAdminPermission]
    user_id: int

    alias: Omittable[str] = Omitted()
