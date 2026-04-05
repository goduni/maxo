from maxo.enums.markup_element_type import MarkupElementType
from maxo.types.markup_element import MarkupElement


# Нет в доке, работает
class HeadingMarkup(MarkupElement):
    """
    Представляет заголовок текста
    """

    type: MarkupElementType = MarkupElementType.HEADING
