from enum import StrEnum


class AttachmentRequestType(StrEnum):
    """Запрос на прикрепление данных к сообщению"""

    AUDIO = "audio"
    CONTACT = "contact"
    FILE = "file"
    IMAGE = "image"
    INLINE_KEYBOARD = "inline_keyboard"
    LOCATION = "location"
    SHARE = "share"
    STICKER = "sticker"
    VIDEO = "video"
