from maxo.enums import ChatType
from maxo.types.base import MaxoType
from maxo.types.chat import Chat
from maxo.types.user import User


class UpdateContext(MaxoType):
    """
    Контекст апдейта: идентификаторы чата и пользователя, при включённом обогащении —
    объекты чата и пользователя, полученные через Bot API.
    """

    chat_id: int | None = None
    user_id: int | None = None
    type: ChatType | None = None
    chat: Chat | None = None
    user: User | None = None

    @property
    def chat_type(self) -> ChatType | None:
        return self.type
