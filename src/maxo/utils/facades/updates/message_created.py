from maxo.routing.updates.message_created import MessageCreated
from maxo.types.message import Message
from maxo.utils.facades.methods.message import MessageMethodsFacade
from maxo.utils.facades.updates.base import BaseUpdateFacade


class MessageCreatedFacade(BaseUpdateFacade[MessageCreated], MessageMethodsFacade):
    @property
    def message(self) -> Message:
        return self._update.message
