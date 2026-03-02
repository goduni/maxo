from enum import StrEnum
from typing import TypeAlias


class AttachmentType(StrEnum):
    """Общая схема, представляющая вложение сообщения"""

    TEXT = "text"  # Самодельное поле
    AUDIO = "audio"
    CONTACT = "contact"
    FILE = "file"
    IMAGE = "image"
    INLINE_KEYBOARD = "inline_keyboard"
    LOCATION = "location"
    SHARE = "share"
    STICKER = "sticker"
    VIDEO = "video"

    # Подражание aiogram
    DOCUMENT = FILE


# Подражание aiogram
ContentType: TypeAlias = AttachmentType
