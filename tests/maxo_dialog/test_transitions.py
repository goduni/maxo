import pytest

from maxo import Ctx, Dispatcher
from maxo.bot.bot import Bot
from maxo.fsm.key_builder import DefaultKeyBuilder
from maxo.fsm.state import State, StatesGroup
from maxo.fsm.storages.memory import SimpleEventIsolation
from maxo.routing.filters.command import CommandStart
from maxo.types.message import Message
from maxo_dialog import (
    Dialog,
    DialogManager,
    StartMode,
    Window,
    setup_dialogs,
)
from maxo_dialog.test_tools import BotClient, MockMessageManager
from maxo_dialog.test_tools.bot_client import FakeBot
from maxo_dialog.test_tools.keyboard import InlineButtonTextLocator
from maxo_dialog.test_tools.memory_storage import JsonMemoryStorage
from maxo_dialog.widgets.kbd import Back, Cancel, Next, Start
from maxo_dialog.widgets.text import Const, Format


class MainSG(StatesGroup):
    start = State()
    next = State()


class SecondarySG(StatesGroup):
    start = State()


async def start(message: Message, ctx: Ctx, dialog_manager: DialogManager):
    await dialog_manager.start(MainSG.start, mode=StartMode.RESET_STACK)


@pytest.fixture
def message_manager() -> MockMessageManager:
    return MockMessageManager()


@pytest.fixture
def dp(message_manager: MockMessageManager):
    key_builder = DefaultKeyBuilder(with_destiny=True)
    event_isolation = SimpleEventIsolation(key_builder=key_builder)
    dp = Dispatcher(
        storage=JsonMemoryStorage(),
        event_isolation=event_isolation,
        key_builder=key_builder,
    )
    dp.message_created.handler(start, CommandStart())
    dp.include(
        Dialog(
            Window(
                Const("First"),
                Next(),
                Start(Const("Start"), state=SecondarySG.start, id="start"),
                Cancel(),
                state=MainSG.start,
            ),
            Window(
                Const("Second"),
                Back(),
                state=MainSG.next,
            ),
        )
    )
    dp.include(
        Dialog(
            Window(
                Format("Subdialog"),
                Cancel(),
                state=SecondarySG.start,
            ),
        )
    )
    setup_dialogs(dp, message_manager=message_manager, events_isolation=event_isolation)
    return dp


@pytest.fixture
def client(dp) -> BotClient:
    return BotClient(dp)


@pytest.fixture
def bot() -> Bot:
    return FakeBot()


@pytest.mark.asyncio
async def test_start(bot, message_manager, client):
    # start
    await client.send("/start")
    first_message = message_manager.one_message()
    assert first_message.unsafe_body.text == "First"
    assert first_message.unsafe_body.keyboard


@pytest.mark.asyncio
async def test_next_back(bot, message_manager, client):
    await client.send("/start")
    first_message = message_manager.one_message()

    # click next
    message_manager.reset_history()
    callback_id = await client.click(
        first_message,
        InlineButtonTextLocator("Next"),
    )
    message_manager.assert_answered(callback_id)
    second_message = message_manager.one_message()
    assert second_message.unsafe_body.text == "Second"

    # click back
    message_manager.reset_history()
    callback_id = await client.click(
        second_message,
        InlineButtonTextLocator("Back"),
    )
    message_manager.assert_answered(callback_id)
    last_message = message_manager.one_message()
    assert last_message.unsafe_body.text == "First"
    assert last_message.unsafe_body.keyboard


@pytest.mark.asyncio
async def test_finish_last(bot, message_manager, client):
    await client.send("/start")
    first_message = message_manager.one_message()

    # click back
    message_manager.reset_history()
    callback_id = await client.click(
        first_message,
        InlineButtonTextLocator("Cancel"),
    )
    message_manager.assert_answered(callback_id)
    last_message = message_manager.one_message()
    assert not last_message.unsafe_body.keyboard, "Keyboard closed"


@pytest.mark.asyncio
async def test_reset_stack(bot, message_manager, client):
    for _ in range(200):
        message_manager.reset_history()
        await client.send("/start")
        first_message = message_manager.one_message()
        assert first_message.text == "First"

    message_manager.reset_history()
    callback_id = await client.click(
        first_message,
        InlineButtonTextLocator("Cancel"),
    )
    message_manager.assert_answered(callback_id)
    last_message = message_manager.one_message()
    assert not last_message.unsafe_body.keyboard, "Keyboard closed"


@pytest.mark.asyncio
async def test_subdialog(bot, message_manager, client):
    await client.send("/start")
    first_message = message_manager.one_message()

    # start subdialog
    message_manager.reset_history()
    callback_id = await client.click(
        first_message,
        InlineButtonTextLocator("Start"),
    )
    message_manager.assert_answered(callback_id)
    second_message = message_manager.one_message()
    assert second_message.unsafe_body.text == "Subdialog"

    # close subdialog
    message_manager.reset_history()
    callback_id = await client.click(
        second_message,
        InlineButtonTextLocator("Cancel"),
    )
    message_manager.assert_answered(callback_id)
    last_message = message_manager.one_message()
    assert last_message.unsafe_body.text == "First"
    assert last_message.unsafe_body.keyboard
