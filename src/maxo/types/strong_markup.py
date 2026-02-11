from maxo.enums.markup_element_type import MarkupElementType
from maxo.types.markup_element import MarkupElement


class StrongMarkup(MarkupElement):
    """
    Представляет **жирный** текст

    Args:
        type:
    """

    type: MarkupElementType = MarkupElementType.STRONG
