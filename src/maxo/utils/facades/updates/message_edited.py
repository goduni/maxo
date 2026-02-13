from maxo.routing.updates.message_edited import MessageEdited
from maxo.types.message import Message
from maxo.utils.facades.methods.message import MessageMethodsFacade
from maxo.utils.facades.updates.base import BaseUpdateFacade


class MessageEditedFacade(
    BaseUpdateFacade[MessageEdited],
    MessageMethodsFacade,
):
    @property
    def message(self) -> Message:
        return self._update.message
