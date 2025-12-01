from dataclasses import dataclass
from typing import Any

from maxo import Bot
from maxo.enums import ChatType
from maxo.routing.signals.exception import ErrorEvent
from maxo.routing.updates import MessageCallback, MessageCreated
from maxo.routing.updates.bot_started import BotStarted
from maxo.types import Chat, User

from .update_event import DialogUpdateEvent

ChatEvent = (
    MessageCreated
    | MessageCallback
    | BotStarted
    | DialogUpdateEvent
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
