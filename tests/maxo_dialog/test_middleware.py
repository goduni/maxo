import pytest

from maxo import Dispatcher
from maxo.bot.bot import Bot
from maxo.dialogs import (
    BotClient,
    Dialog,
    DialogManager,
    FakeBot,
    MockMessageManager,
    StartMode,
    Window,
    setup_dialogs,
)
from maxo.dialogs.test_tools.memory_storage import JsonMemoryStorage
from maxo.dialogs.widgets.text import Format
from maxo.fsm.state import State, StatesGroup
from maxo.routing.ctx import Ctx
from maxo.routing.filters.command import CommandStart
from maxo.routing.interfaces import BaseMiddleware, NextMiddleware
from maxo.routing.updates.base import MaxUpdate
from maxo.types.message import Message


class MainSG(StatesGroup):
    start = State()


class MyMiddleware(BaseMiddleware[MaxUpdate]):
    async def __call__(
        self,
        update: MaxUpdate,
        ctx: Ctx,
        next: NextMiddleware,
    ) -> None:
        ctx["my_key"] = "my_value"
        return await next(ctx)


async def start(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(MainSG.start, mode=StartMode.RESET_STACK)


@pytest.fixture
def message_manager() -> MockMessageManager:
    return MockMessageManager()


@pytest.fixture
def dp(message_manager: MockMessageManager):
    dp = Dispatcher(storage=JsonMemoryStorage())
    dp.message_created.handler(start, CommandStart())
    dp.include(
        Dialog(
            Window(
                Format("{data[my_key]}"),
                state=MainSG.start,
            ),
        ),
    )
    dp.message_created.middleware.outer(MyMiddleware())
    setup_dialogs(dp, message_manager=message_manager)
    return dp


@pytest.fixture
def client(dp) -> BotClient:
    return BotClient(dp)


@pytest.fixture
def bot() -> Bot:
    return FakeBot()


@pytest.mark.asyncio
async def test_middleware(bot, message_manager, client):
    await client.send("/start")
    first_message = message_manager.one_message()
    assert first_message.unsafe_body.text == "my_value"
