from enum import Enum
from typing import Any

from maxo import Bot
from maxo.fsm import State
from maxo.routing.updates import BaseUpdate
from maxo.types import Recipient, User

from .modes import ShowMode, StartMode
from .stack import AccessSettings

DIALOG_EVENT_NAME = "aiogd_update"


class DialogAction(Enum):
    DONE = "DONE"
    START = "START"
    UPDATE = "UPDATE"
    SWITCH = "SWITCH"


class DialogUpdateEvent(BaseUpdate):
    user: User
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
