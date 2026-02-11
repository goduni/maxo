from maxo.enums.markup_element_type import MarkupElementType
from maxo.types.markup_element import MarkupElement


class EmphasizedMarkup(MarkupElement):
    """
    Представляет *курсив*

    Args:
        type:
    """

    type: MarkupElementType = MarkupElementType.EMPHASIZED
