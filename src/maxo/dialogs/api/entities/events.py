from dataclasses import dataclass
from typing import Any

from maxo import Bot
from maxo.enums import ChatType
from maxo.routing.updates import (
    BotAddedToChat,
    BotRemovedFromChat,
    BotStarted,
    BotStopped,
    ErrorEvent,
    MessageCallback,
    MessageCreated,
    UserAddedToChat,
    UserRemovedFromChat,
)
from maxo.types import Chat, User

from .update_event import DialogUpdateEvent

ChatEvent = (
    MessageCreated
    | MessageCallback
    | BotStarted
    | BotStopped
    | DialogUpdateEvent
    | UserAddedToChat
    | UserRemovedFromChat
    | BotAddedToChat
    | BotRemovedFromChat
    | ErrorEvent[Any, Any]
)


@dataclass
class EventContext:
    bot: Bot
    chat_id: int | None
    user_id: int | None
    chat_type: ChatType | None
    user: User | None
    chat: Chat | None


EVENT_CONTEXT_KEY = "aiogd_event_context"
