from maxo.enums.markup_element_type import MarkupElementType
from maxo.omit import Omittable, Omitted
from maxo.types.markup_element import MarkupElement


class UserMentionMarkup(MarkupElement):
    """
    Представляет упоминание пользователя в тексте. Упоминание может быть как по имени пользователя, так и по ID, если у пользователя нет имени

    Args:
        type:
        user_id: ID упомянутого пользователя без имени
        user_link: `@username` упомянутого пользователя
    """

    type: MarkupElementType = MarkupElementType.USER_MENTION

    user_id: Omittable[int | None] = Omitted()
    user_link: Omittable[str | None] = Omitted()
