from datetime import UTC, datetime
from typing import Any

import pytest

from maxo.enums import ChatType
from maxo.routing.ctx import Ctx
from maxo.routing.middlewares.update_context import (
    EVENT_FROM_USER_KEY,
    UPDATE_CONTEXT_KEY,
    UpdateContextMiddleware,
)
from maxo.routing.signals.update import MaxoUpdate
from maxo.routing.updates.message_created import MessageCreated
from maxo.routing.updates.message_removed import MessageRemoved
from maxo.types import Chat, ChatMembersList, Message, MessageBody, Recipient, User


def _make_message_created(chat_id: int = 1, user_id: int = 1) -> MessageCreated:
    return MessageCreated(
        message=Message(
            body=MessageBody(mid="m1", seq=1),
            recipient=Recipient(chat_type=ChatType.CHAT, chat_id=chat_id),
            timestamp=datetime.now(UTC),
            sender=User(
                user_id=user_id,
                first_name="Test",
                is_bot=False,
                last_activity_time=datetime.now(UTC),
            ),
        ),
        timestamp=datetime.now(UTC),
    )


def _make_message_removed(chat_id: int = 1, user_id: int = 2) -> MessageRemoved:
    return MessageRemoved(
        chat_id=chat_id,
        message_id="m1",
        user_id=user_id,
        timestamp=datetime.now(UTC),
    )


async def _run_middleware(
    middleware: UpdateContextMiddleware,
    inner_update: Any,
    ctx: Ctx,
) -> None:
    update = MaxoUpdate(update=inner_update)
    next_called: list[bool] = []

    async def next_handler(c: Ctx) -> Any:
        next_called.append(True)
        return None

    await middleware(update=update, ctx=ctx, next=next_handler)
    assert next_called


@pytest.mark.asyncio
async def test_resolve_message_created_without_enrich() -> None:
    middleware = UpdateContextMiddleware()
    msg = _make_message_created(chat_id=10, user_id=5)
    ctx = Ctx({"update": msg})

    await _run_middleware(middleware, msg, ctx)

    uc = ctx[UPDATE_CONTEXT_KEY]
    assert uc.chat_id == 10
    assert uc.user_id == 5
    assert uc.chat is None
    assert uc.user is msg.message.sender
    assert uc.type == ChatType.CHAT
    assert ctx[EVENT_FROM_USER_KEY] is msg.message.sender


@pytest.mark.asyncio
async def test_resolve_message_removed_without_enrich() -> None:
    middleware = UpdateContextMiddleware()
    removed = _make_message_removed(chat_id=20, user_id=7)
    ctx = Ctx({"update": removed})

    await _run_middleware(middleware, removed, ctx)

    uc = ctx[UPDATE_CONTEXT_KEY]
    assert uc.chat_id == 20
    assert uc.user_id == 7
    assert uc.chat is None
    assert uc.user is None
    assert uc.type is None
    assert EVENT_FROM_USER_KEY not in ctx


@pytest.mark.asyncio
async def test_enrich_disabled_does_not_call_bot() -> None:
    async def get_chat(self: Any, **kwargs: Any) -> None:
        raise AssertionError("get_chat must not be called")

    async def get_members(self: Any, **kwargs: Any) -> None:
        raise AssertionError("get_members must not be called")

    bot = type("Bot", (), {"get_chat": get_chat, "get_members": get_members})()
    middleware = UpdateContextMiddleware(enrich=False)
    msg = _make_message_created()
    ctx = Ctx({"update": msg, "bot": bot})

    await _run_middleware(middleware, msg, ctx)

    uc = ctx[UPDATE_CONTEXT_KEY]
    assert uc.chat is None


@pytest.mark.asyncio
async def test_enrich_enabled_fills_chat_and_user_from_payload() -> None:
    from maxo.enums.chat_status import ChatStatus

    chat_result = Chat(
        chat_id=1,
        is_public=False,
        last_event_time=datetime.now(UTC),
        participants_count=2,
        status=ChatStatus.ACTIVE,
        type=ChatType.CHAT,
    )

    get_chat_called: list[int] = []

    async def get_chat(self: Any, **kwargs: Any) -> Chat:
        get_chat_called.append(kwargs["chat_id"])
        return chat_result

    async def get_members_noop(self: Any, **kwargs: Any) -> ChatMembersList:
        return ChatMembersList(members=[])

    bot = type("Bot", (), {"get_chat": get_chat, "get_members": get_members_noop})()
    middleware = UpdateContextMiddleware(enrich=True)
    msg = _make_message_created(chat_id=1, user_id=5)
    ctx = Ctx({"update": msg, "bot": bot})

    await _run_middleware(middleware, msg, ctx)

    assert get_chat_called == [1]
    uc = ctx[UPDATE_CONTEXT_KEY]
    assert uc.chat is chat_result
    assert uc.type == ChatType.CHAT
    assert uc.user is msg.message.sender
    assert ctx[EVENT_FROM_USER_KEY] is msg.message.sender


@pytest.mark.asyncio
async def test_enrich_message_removed_fills_user_via_get_members() -> None:
    from maxo.enums.chat_status import ChatStatus
    from maxo.types.chat_member import ChatMember

    chat_result = Chat(
        chat_id=1,
        is_public=False,
        last_event_time=datetime.now(UTC),
        participants_count=2,
        status=ChatStatus.ACTIVE,
        type=ChatType.CHAT,
    )
    member = ChatMember(
        user_id=2,
        first_name="Member",
        is_bot=False,
        last_activity_time=datetime.now(UTC),
        alias="",
        is_admin=False,
        is_owner=False,
        join_time=datetime.now(UTC),
        last_access_time=datetime.now(UTC),
    )
    members_list = ChatMembersList(members=[member])

    get_chat_calls: list[int] = []
    get_members_calls: list[tuple[int, list[int]]] = []

    async def get_chat(self: Any, **kwargs: Any) -> Chat:
        get_chat_calls.append(kwargs["chat_id"])
        return chat_result

    async def get_members(self: Any, **kwargs: Any) -> ChatMembersList:
        get_members_calls.append((kwargs["chat_id"], kwargs.get("user_ids") or []))
        return members_list

    bot = type("Bot", (), {"get_chat": get_chat, "get_members": get_members})()
    middleware = UpdateContextMiddleware(enrich=True)
    removed = _make_message_removed(chat_id=1, user_id=2)
    ctx = Ctx({"update": removed, "bot": bot})

    await _run_middleware(middleware, removed, ctx)

    assert get_chat_calls == [1]
    assert get_members_calls == [(1, [2])]
    uc = ctx[UPDATE_CONTEXT_KEY]
    assert uc.chat is chat_result
    assert uc.user is member
    assert ctx[EVENT_FROM_USER_KEY] is member
