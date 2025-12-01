import re
from typing import Protocol

from maxo.types import CallbackKeyboardButton, Message


class InlineButtonLocator(Protocol):
    def find_button(
        self,
        message: Message,
    ) -> CallbackKeyboardButton | None:
        raise NotImplementedError


class InlineButtonTextLocator:
    def __init__(self, regex: str):
        self.regex = re.compile(regex)

    def find_button(
        self,
        message: Message,
    ) -> CallbackKeyboardButton | None:
        if not message.unsafe_body.keyboard:
            return None
        for row in message.unsafe_body.keyboard.buttons:
            for button in row:
                if self.regex.fullmatch(button.text):
                    return button
        return None

    def __repr__(self) -> str:
        return f"InlineButtonTextLocator({self.regex.pattern!r})"


class InlineButtonPositionLocator:
    def __init__(self, row: int, column: int):
        self.row = row
        self.column = column

    def find_button(
        self,
        message: Message,
    ) -> CallbackKeyboardButton | None:
        if not message.unsafe_body.keyboard:
            return None
        try:
            return message.unsafe_body.keyboard.payload.buttons[self.row][self.column]
        except IndexError:
            return None

    def __repr__(self) -> str:
        return f"InlineButtonPositionLocator(row={self.row}, column={self.column})"


class InlineButtonDataLocator:
    def __init__(self, regex: str):
        self.regex = re.compile(regex)

    def find_button(
        self,
        message: Message,
    ) -> CallbackKeyboardButton | None:
        if not message.unsafe_body.keyboard:
            return None
        for row in message.unsafe_body.keyboard.buttons:
            for button in row:
                if not hasattr(button, "payload"):
                    continue
                if self.regex.fullmatch(button.payload):
                    return button
        return None

    def __repr__(self) -> str:
        return f"InlineButtonDataLocator({self.regex.pattern!r})"
