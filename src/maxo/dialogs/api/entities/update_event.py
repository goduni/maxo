from enum import Enum
from typing import Any

from maxo import Bot
from maxo.fsm import State
from maxo.routing.updates.base import MaxUpdate
from maxo.types import Chat, MaxoType, Recipient, User

from .modes import ShowMode, StartMode
from .stack import AccessSettings

DIALOG_EVENT_NAME = "aiogd_update"


class DialogAction(Enum):
    DONE = "DONE"
    START = "START"
    UPDATE = "UPDATE"
    SWITCH = "SWITCH"


class DialogUpdateEvent(MaxoType):
    sender: User
    chat: Chat
    recipient: Recipient
    action: DialogAction
    data: Any
    intent_id: str | None
    stack_id: str | None
    show_mode: ShowMode | None = None
    bot: Bot


class DialogStartEvent(DialogUpdateEvent):
    new_state: State
    mode: StartMode
    access_settings: AccessSettings | None = None


class DialogSwitchEvent(DialogUpdateEvent):
    new_state: State


class DialogUpdate(MaxUpdate):
    aiogd_update: DialogUpdateEvent

    @property
    def type(self) -> str:
        return DIALOG_EVENT_NAME

    @property
    def event(self) -> DialogUpdateEvent:
        return self.aiogd_update
