from enum import StrEnum


class MarkupElementType(StrEnum):
    EMPHASIZED = "emphasized"
    LINK = "link"
    MONOSPACED = "monospaced"
    QUOTE = "quote"
    STRIKETHROUGH = "strikethrough"
    STRONG = "strong"
    UNDERLINE = "underline"
    USER_MENTION = "user_mention"
