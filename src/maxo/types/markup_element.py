from maxo.enums import MarkupElementType
from maxo.types.base import MaxoType


class MarkupElement(MaxoType):
    """
    Args:
        from_: Индекс начала элемента разметки в тексте. Нумерация с нуля
        length: Длина элемента разметки
        type: Тип элемента разметки. Может быть **жирный**,  *курсив*, ~зачеркнутый~, <ins>подчеркнутый</ins>, `моноширинный`, ссылка или упоминание пользователя
    """

    from_: int
    length: int
    type: MarkupElementType
