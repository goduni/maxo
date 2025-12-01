from typing import assert_never

from maxo.enums import ChatType
from maxo.omit import Omittable, Omitted


def calculate_chat_id_and_user_id(
    chat_type: ChatType,
    chat_id: Omittable[int | None],
    user_id: Omittable[int | None],
) -> tuple[Omittable[int], Omittable[int]]:
    if chat_type is ChatType.CHAT:
        return chat_id or Omitted(), Omitted()
    if chat_type is ChatType.DIALOG:
        return chat_id or Omitted(), user_id or Omitted()
    assert_never(chat_type)
