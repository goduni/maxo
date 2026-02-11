from maxo.enums.markup_element_type import MarkupElementType
from maxo.types.markup_element import MarkupElement


class MonospacedMarkup(MarkupElement):
    """
    Представляет `моноширинный` или блок ```код``` в тексте

    Args:
        type:
    """

    type: MarkupElementType = MarkupElementType.MONOSPACED
