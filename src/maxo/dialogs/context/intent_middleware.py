from logging import getLogger
from typing import Any, cast

from maxo.dialogs.api.entities import (
    DEFAULT_STACK_ID,
    EVENT_CONTEXT_KEY,
    ChatEvent,
    Context,
    DialogUpdate,
    DialogUpdateEvent,
    EventContext,
    Stack,
)
from maxo.dialogs.api.exceptions import (
    InvalidStackIdError,
    OutdatedIntent,
    UnknownIntent,
    UnknownState,
)
from maxo.dialogs.api.internal import CONTEXT_KEY, STACK_KEY, STORAGE_KEY
from maxo.dialogs.api.protocols import (
    DialogRegistryProtocol,
    StackAccessValidator,
)
from maxo.dialogs.utils import remove_intent_id
from maxo.enums.chat_type import ChatType
from maxo.fsm.storages.base import BaseEventIsolation, BaseStorage
from maxo.routing.ctx import Ctx
from maxo.routing.interfaces import BaseMiddleware, NextMiddleware
from maxo.routing.middlewares.update_context import (
    EVENT_FROM_USER_KEY,
    UPDATE_CONTEXT_KEY,
)
from maxo.routing.sentinels import UNHANDLED
from maxo.routing.signals.exception import ErrorEvent
from maxo.routing.updates.base import MaxUpdate
from maxo.routing.updates.bot_started import BotStarted
from maxo.routing.updates.message_callback import MessageCallback
from maxo.routing.updates.message_created import MessageCreated
from maxo.utils.facades import MessageCallbackFacade

from .storage import StorageProxy

logger = getLogger(__name__)

FORBIDDEN_STACK_KEY = "aiogd_stack_forbidden"


def event_context_from_callback(event: MessageCallback, ctx: Ctx) -> EventContext:
    return EventContext(
        bot=ctx["bot"],
        user=event.callback.user,
        user_id=event.callback.user.user_id,
        chat_id=event.unsafe_message.recipient.chat_id,
        chat=None,
        chat_type=event.unsafe_message.recipient.chat_type,
    )


def event_context_from_message(event: MessageCreated, ctx: Ctx) -> EventContext:
    user = ctx.get(EVENT_FROM_USER_KEY)
    _event_user_id = getattr(event.message.sender, "user_id", None)
    user_id = _event_user_id or getattr(user, "user_id", None)
    return EventContext(
        bot=ctx["bot"],
        user=user,
        user_id=user_id,
        chat=None,
        chat_id=event.message.recipient.chat_id,
        chat_type=event.message.recipient.chat_type,
    )


def event_context_from_bot_started(event: BotStarted, ctx: Ctx) -> EventContext:
    return EventContext(
        bot=ctx["bot"],
        user=event.user,
        user_id=event.user.user_id,
        chat_id=event.chat_id,
        chat_type=ChatType.DIALOG,
        chat=None,
    )


def event_context_from_aiogd(event: DialogUpdateEvent) -> EventContext:
    return EventContext(
        bot=event.bot,
        user=event.sender,
        user_id=event.sender.user_id,
        chat=event.chat,
        chat_id=event.chat.chat_id,
        chat_type=event.chat.type,
    )


def event_context_from_error(event: ErrorEvent, ctx: Ctx) -> EventContext:
    if isinstance(event.event, MessageCreated):
        return event_context_from_message(event.event, ctx)
    if isinstance(event.event, MessageCallback):
        return event_context_from_callback(event.event, ctx)
    if isinstance(event.event, DialogUpdate) and event.event.aiogd_update:
        return event_context_from_aiogd(event.event.aiogd_update)
    if isinstance(event.event, BotStarted):
        return event_context_from_bot_started(event.event, ctx)
    raise ValueError(f"Unsupported event type in ErrorEvent.update: {event.event}")


class IntentMiddlewareFactory:
    def __init__(
        self,
        registry: DialogRegistryProtocol,
        access_validator: StackAccessValidator,
        events_isolation: BaseEventIsolation,
    ) -> None:
        super().__init__()
        self.registry = registry
        self.access_validator = access_validator
        self.events_isolation = events_isolation

    def storage_proxy(
        self,
        event_context: EventContext,
        fsm_storage: BaseStorage,
    ) -> StorageProxy:
        return StorageProxy(
            bot=event_context.bot,
            storage=fsm_storage,
            events_isolation=self.events_isolation,
            state_groups=self.registry.states_groups(),
            user_id=event_context.user.id,
            chat_id=event_context.chat_id,
        )

    def _check_outdated(self, intent_id: str, stack: Stack) -> None:
        """Check if intent id is outdated for stack."""
        if stack.empty():
            raise OutdatedIntent(
                stack.id,
                f"Outdated intent id ({intent_id}) for stack ({stack.id})",
            )
        if intent_id != stack.last_intent_id():
            raise OutdatedIntent(
                stack.id,
                f"Outdated intent id ({intent_id}) for stack ({stack.id})",
            )

    async def _load_stack(
        self,
        stack_id: str | None,
        proxy: StorageProxy,
    ) -> Stack | None:
        if stack_id is None:
            raise InvalidStackIdError("Both stack id and intent id are None")
        return await proxy.load_stack(stack_id)

    async def _load_context_by_stack(
        self,
        event: ChatEvent,
        proxy: StorageProxy,
        stack_id: str | None,
        ctx: Ctx,
    ) -> None:
        logger.debug(
            "Loading context for stack: `%s`, user: `%s`, chat: `%s`",
            stack_id,
            proxy.user_id,
            proxy.chat_id,
        )
        stack = await self._load_stack(stack_id, proxy)
        if not stack:
            return
        if stack.empty():
            context = None
        else:
            try:
                context = await proxy.load_context(stack.last_intent_id())
            except:
                await proxy.unlock()
                raise

        if not await self.access_validator.is_allowed(
            stack,
            context,
            event,
            ctx,
        ):
            logger.debug(
                "Stack %s is not allowed for user %s",
                stack.id,
                proxy.user_id,
            )
            ctx[FORBIDDEN_STACK_KEY] = True
            await proxy.unlock()
            return

        ctx[STORAGE_KEY] = proxy
        ctx[STACK_KEY] = stack
        ctx[CONTEXT_KEY] = context

    async def _load_context_by_intent(
        self,
        event: ChatEvent,
        proxy: StorageProxy,
        intent_id: str,
        ctx: Ctx,
    ) -> None:
        logger.debug(
            "Loading context for intent: `%s`, user: `%s`, chat: `%s`",
            intent_id,
            proxy.user_id,
            proxy.chat_id,
        )
        context = await proxy.load_context(intent_id)
        stack = await self._load_stack(context.stack_id, proxy)
        if not stack:
            return
        try:
            self._check_outdated(intent_id, stack)
        except:
            await proxy.unlock()
            raise

        if not await self.access_validator.is_allowed(
            stack,
            context,
            event,
            ctx,
        ):
            logger.debug(
                "Stack %s is not allowed for user %s",
                stack.id,
                proxy.user_id,
            )
            ctx[FORBIDDEN_STACK_KEY] = True
            await proxy.unlock()
            return

        ctx[STORAGE_KEY] = proxy
        ctx[STACK_KEY] = stack
        ctx[CONTEXT_KEY] = context

    async def _load_default_context(
        self,
        event: ChatEvent,
        ctx: Ctx,
        event_context: EventContext,
    ) -> None:
        return await self._load_context_by_stack(
            event=event,
            proxy=self.storage_proxy(event_context, ctx["fsm_storage"]),
            stack_id=DEFAULT_STACK_ID,
            ctx=ctx,
        )

    async def process_message(
        self,
        update: MessageCreated,
        ctx: Ctx,
        next: NextMiddleware,
    ) -> Any:
        event_context = event_context_from_message(update, ctx)
        ctx[EVENT_CONTEXT_KEY] = event_context
        await self._load_default_context(update, ctx, event_context)
        return await next(ctx)

    async def process_aiogd_update(
        self,
        update: DialogUpdateEvent,
        ctx: Ctx,
        next: NextMiddleware,
    ) -> Any:
        event_context = event_context_from_aiogd(update)
        ctx[EVENT_CONTEXT_KEY] = event_context

        if update.intent_id:
            await self._load_context_by_intent(
                event=update,
                proxy=self.storage_proxy(event_context, ctx["fsm_storage"]),
                intent_id=update.intent_id,
                ctx=ctx,
            )
        else:
            await self._load_context_by_stack(
                event=update,
                proxy=self.storage_proxy(event_context, ctx["fsm_storage"]),
                stack_id=update.stack_id,
                ctx=ctx,
            )
        return await next(ctx)

    async def process_callback(
        self,
        update: MessageCallback,
        ctx: Ctx,
        next: NextMiddleware,
    ) -> Any:
        if UPDATE_CONTEXT_KEY not in ctx:
            return await next(ctx)

        event_context = event_context_from_callback(update, ctx)
        ctx[EVENT_CONTEXT_KEY] = event_context
        original_data = update.callback.payload
        if original_data:
            intent_id, _ = remove_intent_id(original_data)
            if intent_id:
                await self._load_context_by_intent(
                    event=update,
                    proxy=self.storage_proxy(event_context, ctx["fsm_storage"]),
                    intent_id=intent_id,
                    ctx=ctx,
                )
            else:
                await self._load_default_context(update, ctx, event_context)
            ctx["payload"] = original_data
        else:
            await self._load_default_context(update, ctx, event_context)
        result = await next(ctx)
        if result is UNHANDLED and ctx.get(FORBIDDEN_STACK_KEY):
            facade = cast(MessageCallbackFacade, ctx["facade"])
            await facade.callback_answer(notification="")
        return result

    async def process_bot_started(
        self,
        update: BotStarted,
        ctx: Ctx,
        next: NextMiddleware,
    ) -> Any:
        if UPDATE_CONTEXT_KEY not in ctx:
            return await next(ctx)

        event_context = event_context_from_bot_started(update, ctx)
        ctx[EVENT_CONTEXT_KEY] = event_context
        await self._load_default_context(update, ctx, event_context)
        return await next(ctx)


SUPPORTED_ERROR_EVENTS = (
    MessageCreated,
    MessageCallback,
    BotStarted,
    DialogUpdateEvent,
    ErrorEvent,
)


async def context_saver_middleware(
    update: MaxUpdate,
    ctx: Ctx,
    next: NextMiddleware,
) -> Any:
    result = await next(ctx)
    proxy: StorageProxy = ctx.get(STORAGE_KEY)
    if proxy:
        await proxy.save_context(ctx.get(CONTEXT_KEY))
        await proxy.save_stack(ctx.get(STACK_KEY))
    return result


async def context_unlocker_middleware(
    update: MaxUpdate,
    ctx: Ctx,
    next: NextMiddleware,
) -> Any:
    proxy: StorageProxy = ctx.get(STORAGE_KEY)
    try:
        result = await next(ctx)
    finally:
        if proxy:
            await proxy.unlock()
    return result


class IntentErrorMiddleware(BaseMiddleware[ErrorEvent]):
    def __init__(
        self,
        registry: DialogRegistryProtocol,
        access_validator: StackAccessValidator,
        events_isolation: BaseEventIsolation,
    ) -> None:
        super().__init__()
        self.registry = registry
        self.events_isolation = events_isolation
        self.access_validator = access_validator

    def _is_error_supported(
        self,
        event: ErrorEvent,
        ctx: Ctx,
    ) -> bool:
        update = event.update.update
        if isinstance(update, InvalidStackIdError):
            return False
        if not isinstance(update, SUPPORTED_ERROR_EVENTS):
            return False
        if UPDATE_CONTEXT_KEY not in ctx:
            return False
        if EVENT_FROM_USER_KEY not in ctx:  # noqa: SIM103
            return False
        return True

    async def _fix_broken_stack(
        self,
        storage: StorageProxy,
        stack: Stack,
    ) -> None:
        while not stack.empty():
            await storage.remove_context(stack.pop())
        await storage.save_stack(stack)

    async def _load_last_context(
        self,
        storage: StorageProxy,
        stack: Stack,
    ) -> Context | None:
        try:
            return await storage.load_context(stack.last_intent_id())
        except (UnknownIntent, OutdatedIntent):
            logger.warning(
                "Stack is broken for user %s, chat %s, resetting",
                storage.user_id,
                storage.chat_id,
            )
            await self._fix_broken_stack(storage, stack)
        return None

    async def _load_stack(
        self,
        proxy: StorageProxy,
        error: Exception,
    ) -> Stack:
        if isinstance(error, OutdatedIntent):
            return await proxy.load_stack(stack_id=error.stack_id)
        return await proxy.load_stack()

    async def __call__(
        self,
        update: ErrorEvent,
        ctx: Ctx,
        next: NextMiddleware,
    ) -> Any:
        error = update.error
        if not self._is_error_supported(update, ctx):
            return await next(ctx)

        try:
            event_context = event_context_from_error(update, ctx)
            ctx[EVENT_CONTEXT_KEY] = event_context
            proxy = StorageProxy(
                bot=event_context.bot,
                storage=ctx["fsm_storage"],
                events_isolation=self.events_isolation,
                state_groups=self.registry.states_groups(),
                user_id=event_context.user.id,
                chat_id=event_context.chat_id,
            )
            ctx[STORAGE_KEY] = proxy
            stack = await self._load_stack(proxy, update.error)
            if stack.empty() or isinstance(error, UnknownState):
                context = None
            else:
                context = await self._load_last_context(
                    storage=proxy,
                    stack=stack,
                )

            if await self.access_validator.is_allowed(
                stack,
                context,
                update.update.update,
                ctx,
            ):
                ctx[STACK_KEY] = stack
                ctx[CONTEXT_KEY] = context
            else:
                logger.debug(
                    "Stack %s is not allowed for user %s",
                    stack.id,
                    proxy.user_id,
                )
                ctx[FORBIDDEN_STACK_KEY] = True
                await proxy.unlock()
            return await next(ctx)
        finally:
            proxy: StorageProxy = ctx.get(STORAGE_KEY)
            if proxy:
                await proxy.unlock()
                context = ctx.get(CONTEXT_KEY)
                if context is not None:
                    await proxy.save_context(context)
                await proxy.save_stack(ctx.get(STACK_KEY))
