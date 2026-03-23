"""Демонстрация maxo.dialogs.test_tools.

Запуск: python examples/dialogs_testing.py
Не требует токена бота или базы данных.
"""
from __future__ import annotations

import asyncio
from typing import Any

from maxo import Dispatcher
from maxo.dialogs import Dialog, DialogManager, StartMode, Window, setup_dialogs
from maxo.dialogs.test_tools import BotClient, MockMessageManager
from maxo.dialogs.test_tools.keyboard import InlineButtonTextLocator
from maxo.dialogs.test_tools.memory_storage import JsonMemoryStorage
from maxo.dialogs.widgets.kbd import Back, Button
from maxo.dialogs.widgets.text import Const
from maxo.fsm import State, StatesGroup
from maxo.fsm.key_builder import DefaultKeyBuilder
from maxo.fsm.storages.memory import SimpleEventIsolation
from maxo.routing.filters import CommandStart
from maxo.routing.signals import AfterStartup, BeforeStartup
from maxo.routing.updates import MessageCreated


class MenuSG(StatesGroup):
    main = State()
    detail = State()


async def on_detail(
    callback: Any,
    button: Any,
    manager: DialogManager,
) -> None:
    await manager.switch_to(MenuSG.detail)


dialog = Dialog(
    Window(
        Const("Главное меню"),
        Button(Const("Подробнее"), id="detail", on_click=on_detail),
        state=MenuSG.main,
    ),
    Window(
        Const("Детальная страница"),
        Back(),
        state=MenuSG.detail,
    ),
)

key_builder = DefaultKeyBuilder(with_destiny=True)
dp = Dispatcher(key_builder=key_builder)


@dp.message_created(CommandStart())
async def start_handler(
    message: MessageCreated,
    dialog_manager: DialogManager,
) -> None:
    await dialog_manager.start(MenuSG.main, mode=StartMode.RESET_STACK)


def make_env() -> tuple[Dispatcher, BotClient, MockMessageManager]:
    storage = JsonMemoryStorage()
    message_manager = MockMessageManager()
    key_builder = DefaultKeyBuilder(with_destiny=True)
    event_isolation = SimpleEventIsolation(key_builder=key_builder)

    test_dp = Dispatcher(
        storage=storage,
        events_isolation=event_isolation,
        key_builder=key_builder,
    )
    test_dp.message_created.handler(start_handler, CommandStart())
    test_dp.include(dialog)
    setup_dialogs(
        test_dp,
        message_manager=message_manager,
        events_isolation=event_isolation,
    )

    client = BotClient(test_dp)
    return test_dp, client, message_manager


async def startup(dp: Dispatcher, client: BotClient) -> None:
    await dp.feed_signal(BeforeStartup(), client.bot)
    await dp.feed_signal(AfterStartup(), client.bot)


async def demo_render_window() -> None:
    test_dp, client, mm = make_env()
    await startup(test_dp, client)

    await client.send("/start")

    msg = mm.last_message()
    assert msg.body.text == "Главное меню", f"Unexpected text: {msg.body.text!r}"
    assert msg.body.keyboard is not None
    buttons = [btn.text for row in msg.body.keyboard.buttons for btn in row]
    assert "Подробнее" in buttons, f"Button not found, got: {buttons}"
    print("demo_render_window: OK")


async def demo_render_transition() -> None:
    test_dp, client, mm = make_env()
    await startup(test_dp, client)

    await client.send("/start")
    menu_msg = mm.last_message()
    mm.reset_history()

    callback_id = await client.click(menu_msg, InlineButtonTextLocator("Подробнее"))
    mm.assert_answered(callback_id)

    detail_msg = mm.last_message()
    assert detail_msg.body.text == "Детальная страница", (
        f"Unexpected text: {detail_msg.body.text!r}"
    )
    print("demo_render_transition: OK")


async def main() -> None:
    await demo_render_window()
    await demo_render_transition()
    print("All demos passed.")


if __name__ == "__main__":
    asyncio.run(main())
