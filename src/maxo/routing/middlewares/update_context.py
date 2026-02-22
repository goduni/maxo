from typing import Any, Final

from maxo import loggers
from maxo.enums import ChatType
from maxo.omit import is_defined
from maxo.routing.ctx import Ctx
from maxo.routing.interfaces.middleware import BaseMiddleware, NextMiddleware
from maxo.routing.signals.update import MaxoUpdate
from maxo.routing.updates.bot_added_to_chat import BotAddedToChat
from maxo.routing.updates.bot_removed_from_chat import BotRemovedFromChat
from maxo.routing.updates.bot_started import BotStarted
from maxo.routing.updates.bot_stopped import BotStopped
from maxo.routing.updates.chat_title_changed import ChatTitleChanged
from maxo.routing.updates.dialog_cleared import DialogCleared
from maxo.routing.updates.dialog_muted import DialogMuted
from maxo.routing.updates.dialog_removed import DialogRemoved
from maxo.routing.updates.dialog_unmuted import DialogUnmuted
from maxo.routing.updates.message_callback import MessageCallback
from maxo.routing.updates.message_created import MessageCreated
from maxo.routing.updates.message_edited import MessageEdited
from maxo.routing.updates.message_removed import MessageRemoved
from maxo.routing.updates.user_added_to_chat import UserAddedToChat
from maxo.routing.updates.user_removed_from_chat import UserRemovedFromChat
from maxo.types import User
from maxo.types.update_context import UpdateContext

UPDATE_CONTEXT_KEY: Final = "update_context"
EVENT_FROM_USER_KEY: Final = "event_from_user"

_EVENTS_WITH_CHAT_AND_USER = (
    BotAddedToChat,
    BotRemovedFromChat,
    BotStarted,
    BotStopped,
    ChatTitleChanged,
    DialogCleared,
    DialogMuted,
    DialogRemoved,
    DialogUnmuted,
    UserAddedToChat,
    UserRemovedFromChat,
)


class UpdateContextMiddleware(BaseMiddleware[MaxoUpdate[Any]]):
    """
    Мидлварь, заполняющий контекст апдейта (chat_id, user_id, при обогащении — chat, user).

    Args:
        enrich: при True запрашивать чат и при необходимости пользователя через Bot API.
        Можно также передать enrich_update_context=True в workflow_data (например при LongPolling.run).
    """

    def __init__(self, enrich: bool = False) -> None:
        self._enrich = enrich

    async def __call__(
        self,
        update: MaxoUpdate[Any],
        ctx: Ctx,
        next: NextMiddleware[MaxoUpdate[Any]],
    ) -> Any:
        update_context = self._resolve_update_context(update.update)
        ctx[UPDATE_CONTEXT_KEY] = update_context

        user = self._resolve_user(update.update)
        if user is not None:
            ctx[EVENT_FROM_USER_KEY] = user
            update_context.user = user

        do_enrich = self._enrich or ctx.get("enrich_update_context", False)
        if do_enrich and "bot" in ctx:
            await self._enrich_context(ctx, update_context, update.update)
        if update_context.user is not None and EVENT_FROM_USER_KEY not in ctx:
            ctx[EVENT_FROM_USER_KEY] = update_context.user

        return await next(ctx)

    async def _enrich_context(
        self, ctx: Ctx, update_context: UpdateContext, update: Any
    ) -> None:
        """Дополняет контекст данными чата и пользователя через Bot API."""
        bot = ctx["bot"]
        if update_context.chat_id is None:
            return
        logger = loggers.update_context
        try:
            logger.debug("Обогащение контекста: chat_id=%s", update_context.chat_id)
            chat = await bot.get_chat(chat_id=update_context.chat_id)
            update_context.chat = chat
            update_context.type = chat.type
        except Exception as exc:
            logger.warning("Не удалось обогатить контекст: %s", exc, exc_info=True)
            return
        if (
            update_context.user_id is not None
            and update_context.user is None
            and isinstance(update, MessageRemoved)
        ):
            if update_context.chat is not None and update_context.chat.type == ChatType.CHAT:
                try:
                    members_list = await bot.get_members(
                        chat_id=update_context.chat_id,
                        user_ids=[update_context.user_id],
                    )
                    if members_list.members:
                        update_context.user = members_list.members[0]
                except Exception as exc:
                    logger.warning("Не удалось загрузить участника чата: %s", exc, exc_info=True)
            elif (
                update_context.chat is not None
                and update_context.chat.type == ChatType.DIALOG
                and is_defined(update_context.chat.dialog_with_user)
            ):
                update_context.user = update_context.chat.unsafe_dialog_with_user

    def _resolve_update_context(self, update: Any) -> UpdateContext:
        chat_id = None
        user_id = None
        chat_type: ChatType | None = None

        if isinstance(update, _EVENTS_WITH_CHAT_AND_USER):
            chat_id = update.chat_id
            user_id = update.user.user_id
            if hasattr(update, "is_channel"):
                chat_type = ChatType.CHANNEL if update.is_channel else ChatType.CHAT
        elif isinstance(update, MessageCallback):
            user_id = update.user.user_id
            if update.message is not None:
                chat_id = (
                    update.message.recipient.chat_id or update.message.recipient.user_id
                )
                chat_type = update.message.recipient.chat_type
        elif isinstance(update, (MessageEdited, MessageCreated)):
            user_id = (
                update.message.sender.user_id
                if is_defined(update.message.sender)
                else None
            )
            if update.message is not None:
                chat_id = (
                    update.message.recipient.chat_id or update.message.recipient.user_id
                )
                chat_type = update.message.recipient.chat_type
        elif isinstance(update, MessageRemoved):
            chat_id = update.chat_id
            user_id = update.user_id
            chat_type = None

        return UpdateContext(chat_id=chat_id, user_id=user_id, type=chat_type)

    def _resolve_user(self, update: Any) -> User | None:
        if isinstance(update, MessageCreated) and is_defined(update.message.sender):
            return update.message.sender
        if isinstance(update, MessageEdited) and is_defined(update.message.sender):
            return update.message.sender
        if isinstance(update, MessageCallback):
            return update.callback.user
        if isinstance(update, _EVENTS_WITH_CHAT_AND_USER):
            return update.user
        return None
