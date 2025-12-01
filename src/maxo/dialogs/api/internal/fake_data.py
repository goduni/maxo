from typing import Any, Literal

from maxo.bot.methods import CallbackAnswer
from maxo.types import (
    Callback,
    Message,
    Recipient,
    User,
)


class ReplyCallback(Callback):
    original_message: Message

    def answer(self, *_: Any, **__: Any) -> CallbackAnswer:
        raise ValueError(
            "This callback query is generated from ReplyButton click. "
            "Support of `.answer()` call is impossible.",
        )


class FakeUser(User):
    fake: Literal[True] = True


class FakeRecipient(Recipient):
    fake: Literal[True] = True
