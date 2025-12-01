from typing import Any, Final

from maxo.enums import ChatType
from maxo.omit import is_defined
from maxo.routing.ctx import Ctx
from maxo.routing.interfaces.middleware import BaseMiddleware, NextMiddleware
from maxo.routing.signals.update import Update
from maxo.routing.updates.bot_added import BotAdded
from maxo.routing.updates.bot_removed import BotRemoved
from maxo.routing.updates.bot_started import BotStarted
from maxo.routing.updates.chat_title_changed import ChatTitileChanged
from maxo.routing.updates.message_callback import MessageCallback
from maxo.routing.updates.message_chat_created import MessageChatCreated
from maxo.routing.updates.message_created import MessageCreated
from maxo.routing.updates.message_edited import MessageEdited
from maxo.routing.updates.user_added import UserAdded
from maxo.routing.updates.user_removed import UserRemoved
from maxo.types import User
from maxo.types.update_context import UpdateContext

UPDATE_CONTEXT_KEY: Final = "update_context"
EVENT_FROM_USER_KEY: Final = "event_from_user"


# TODO: Определять UpdateContext и User в одном методе
class UpdateContextMiddleware(BaseMiddleware[Update[Any]]):
    async def __call__(
        self,
        update: Update[Any],
        ctx: Ctx,
        next: NextMiddleware[Update[Any]],
    ) -> Any:
        update_context = self._resolve_update_context(update.update)
        ctx[UPDATE_CONTEXT_KEY] = update_context

        user = self._resolve_user(update.update)
        if user is not None:
            ctx[EVENT_FROM_USER_KEY] = user

        return await next(ctx)

    def _resolve_update_context(self, update: Any) -> UpdateContext:
        chat_id = None
        user_id = None

        if isinstance(
            update,
            (
                BotAdded,
                BotRemoved,
                BotStarted,
                ChatTitileChanged,
                UserAdded,
                UserRemoved,
            ),
        ):
            chat_id = update.chat_id
            user_id = update.user.user_id
        elif isinstance(update, MessageCallback):
            user_id = update.user.user_id
            if update.message is not None and update.message.body is not None:
                chat_id = (
                    update.message.recipient.chat_id or update.message.recipient.user_id
                )

        elif isinstance(update, MessageChatCreated):
            chat_id = update.chat.chat_id
        elif isinstance(update, (MessageEdited, MessageCreated)):
            user_id = (
                update.message.sender.user_id
                if is_defined(update.message.sender)
                else None
            )

            if update.message and update.message.body is not None:
                chat_id = (
                    update.message.recipient.chat_id or update.message.recipient.user_id
                )

        return UpdateContext(
            chat_id=chat_id,
            user_id=user_id,
            type=ChatType.DIALOG,
        )

    def _resolve_user(
        self,
        update: Any,
    ) -> User | None:
        if isinstance(update, MessageCreated):
            return update.message.sender
        if isinstance(update, MessageCallback):
            return update.callback.user
        if isinstance(update, BotStarted):
            return update.user
        # TODO: Остальные ивенты
        return None
