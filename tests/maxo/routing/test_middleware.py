from datetime import datetime
from typing import Any, Literal

import pytest

from maxo.enums import ChatType
from maxo.routing.dispatcher import Dispatcher
from maxo.routing.ctx import Ctx
from maxo.routing.routers.simple import Router
from maxo.routing.sentinels import UNHANDLED
from maxo.routing.updates.message_created import MessageCreated
from maxo.routing.signals.update import Update
from maxo.types import Message, User, Recipient


class MockBotInfo:
    def __init__(self, user_id: int):
        self.user_id = user_id


class MockBotState:
    def __init__(self, user_id: int):
        self.info = MockBotInfo(user_id)


class MockBot:
    def __init__(self, user_id: int = 1):
        self.state = MockBotState(user_id)


@pytest.mark.asyncio
async def test_middleware_execution_order():
    router = Router()

    async def handler(update, ctx) -> Any:
        ctx["execution_order"].append("handler")
        return "OK"

    async def outer_middleware_1(update, ctx, next) -> Any:
        ctx["execution_order"].append("outer_middleware_1_pre")
        result = await next(ctx)
        ctx["execution_order"].append("outer_middleware_1_post")
        return result

    async def outer_middleware_2(update, ctx, next) -> Any:
        ctx["execution_order"].append("outer_middleware_2_pre")
        result = await next(ctx)
        ctx["execution_order"].append("outer_middleware_2_post")
        return result

    async def inner_middleware_1(update, ctx, next) -> Any:
        ctx["execution_order"].append("inner_middleware_1_pre")
        result = await next(ctx)
        ctx["execution_order"].append("inner_middleware_1_post")
        return result

    async def inner_middleware_2(update, ctx, next) -> Any:
        ctx["execution_order"].append("inner_middleware_2_pre")
        result = await next(ctx)
        ctx["execution_order"].append("inner_middleware_2_post")
        return result

    router.message_created.handler(handler)
    router.message_created.middleware.outer.add(outer_middleware_1, outer_middleware_2)
    router.message_created.middleware.inner.add(inner_middleware_1, inner_middleware_2)

    update = MessageCreated(
        message=Message(
            recipient=Recipient(chat_type=ChatType.DIALOG, chat_id=1),
            timestamp=datetime.now(),
            sender=User(
                user_id=1,
                first_name="Test",
                is_bot=False,
                last_activity_time=datetime.now(),
            ),
        ),
        timestamp=datetime.now(),
    )
    ctx = Ctx({"execution_order": [], "update": update, "bot": MockBot()})
    ctx["ctx"] = ctx

    result = await router.trigger(ctx)

    assert result == "OK"
    assert ctx["execution_order"] == [
        "outer_middleware_1_pre",
        "outer_middleware_2_pre",
        "inner_middleware_1_pre",
        "inner_middleware_2_pre",
        "handler",
        "inner_middleware_2_post",
        "inner_middleware_1_post",
        "outer_middleware_2_post",
        "outer_middleware_1_post",
    ]


@pytest.mark.asyncio
async def test_middleware_execution_before_observer_filter():
    router = Dispatcher()

    async def update_filter(update, ctx) -> Literal[False]:
        ctx["execution_order"].append("filter")
        return False

    async def handler(update, ctx) -> Any:
        ctx["execution_order"].append("handler")
        return "OK"

    async def outer_middleware_1(update, ctx, next) -> Any:
        ctx["execution_order"].append("outer_middleware_1_pre")
        result = await next(ctx)
        ctx["execution_order"].append("outer_middleware_1_post")
        return result

    router.message_created.filter(update_filter)
    router.message_created.handler(handler)
    router.message_created.middleware.outer.add(outer_middleware_1)

    update = MessageCreated(
        message=Message(
            recipient=Recipient(chat_type=ChatType.DIALOG, chat_id=1),
            timestamp=datetime.now(),
            sender=User(
                user_id=1,
                first_name="Test",
                is_bot=False,
                last_activity_time=datetime.now(),
            ),
        ),
        timestamp=datetime.now(),
    )
    ctx = Ctx({"execution_order": [], "update": update, "bot": MockBot()})
    ctx["ctx"] = ctx

    result = await router.trigger(ctx)

    assert result is UNHANDLED
    assert ctx["execution_order"] == [
        "outer_middleware_1_pre",
        "filter",
        "outer_middleware_1_post",
    ]


@pytest.mark.asyncio
async def test_filter_on_update():
    router = Dispatcher()

    async def update_filter(update, ctx) -> Literal[False]:
        ctx["execution_order"].append("filter")
        return False

    async def handler(update, ctx) -> Any:
        return "OK"

    router.update.filter(update_filter)
    router.message_created.handler(handler)

    update = Update(
        update=MessageCreated(
            message=Message(
                recipient=Recipient(chat_type=ChatType.DIALOG, chat_id=1),
                timestamp=datetime.now(),
                sender=User(
                    user_id=1,
                    first_name="Test",
                    is_bot=False,
                    last_activity_time=datetime.now(),
                ),
            ),
            timestamp=datetime.now(),
        )
    )
    ctx = Ctx({"execution_order": [], "update": update, "bot": MockBot()})
    ctx["ctx"] = ctx

    result = await router.trigger(ctx)

    assert result == UNHANDLED
    assert ctx["execution_order"] == [
        "filter",
    ]
