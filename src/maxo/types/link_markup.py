from maxo.enums.markup_element_type import MarkupElementType
from maxo.types.markup_element import MarkupElement


class LinkMarkup(MarkupElement):
    """
    Представляет ссылку в тексте

    Args:
        type:
        url: URL ссылки
    """

    type: MarkupElementType = MarkupElementType.LINK

    url: str
