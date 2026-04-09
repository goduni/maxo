from enum import StrEnum


class ChatType(StrEnum):
    """Тип чата: диалог, чат"""

    CHANNEL = "channel"
    CHAT = "chat"
    DIALOG = "dialog"

    PRIVATE = DIALOG  # Подражаение aiogram
    GROUP = CHAT  # Подражаение aiogram
    SUPERGROUP = CHAT  # Подражаение aiogram
