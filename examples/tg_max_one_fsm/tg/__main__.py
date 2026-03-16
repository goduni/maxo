import asyncio
import logging
import os
from pathlib import Path

from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.base import DefaultKeyBuilder
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from ..ids import SharedId
from ..user_repo import DbUser, UserRepo
from .current_user import CurrentUserMiddleware
from .fsm_context import SharedFSMContextMiddleware

router = Router()


class MyStates(StatesGroup):
    state1 = State()
    state2 = State()


def get_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Перейти в состояние 1", callback_data="to_state_1")
    builder.button(text="Перейти в состояние 2", callback_data="to_state_2")
    builder.button(text="Очистить состояние", callback_data="clear_state")
    builder.adjust(2)
    return builder.as_markup()


@router.message(CommandStart())
async def start_handler(
    message: Message,
    current_user: DbUser,
    state: FSMContext,
) -> None:
    current_state = await state.get_state()

    await message.answer(
        (
            f"Ваш общий ID: {current_user.shared_id}\n\n"
            f"Отправьте эту команду боту Max: /link {current_user.shared_id}\n\n"
            "Или отправьте эту команду этому боту из другого аккаунта, "
            "чтобы связать их: /link <shared_id>"
        ),
    )
    await message.answer(
        f"Ваше текущее состояние: {current_state}",
        reply_markup=get_keyboard(),
    )


@router.message(Command("state"))
async def get_state_handler(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    await message.answer(f"Ваше текущее состояние: {current_state}")


@router.message(Command("link"))
async def handle_deeplink(
    message: Message,
    command: CommandObject,
    user_repo: UserRepo,
    current_user: DbUser,
) -> None:
    try:
        shared_id_to_link = SharedId(int(command.args))
        await user_repo.link_accounts(
            current_user=current_user,
            shared_id_to_link=shared_id_to_link,
        )
        await message.answer("Аккаунты успешно связаны!")
    except (IndexError, ValueError, TypeError):
        await message.answer("Использование: /link <shared_id>")


@router.callback_query(F.data == "to_state_1")
async def to_state_1(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(MyStates.state1)
    current_state = await state.get_state()
    await callback.message.edit_text(
        f"Ваше текущее состояние: {current_state}",
        reply_markup=get_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data == "to_state_2")
async def to_state_2(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(MyStates.state2)
    current_state = await state.get_state()
    await callback.message.edit_text(
        f"Ваше текущее состояние: {current_state}",
        reply_markup=get_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data == "clear_state")
async def clear_state(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    current_state = await state.get_state()
    await callback.message.edit_text(
        f"Состояние очищено. Ваше текущее состояние: {current_state}",
        reply_markup=get_keyboard(),
    )
    await callback.answer()


async def main() -> None:
    token = os.environ["TG_TOKEN"]
    redis_url = os.environ["REDIS_URL"]

    db_path = (Path(__file__).parent.parent / "db.sqlite").resolve()
    user_repo = UserRepo(db_path)
    await user_repo.create_table()

    key_builder = DefaultKeyBuilder(prefix="fsm", separator=":", with_bot_id=False)
    storage = RedisStorage.from_url(url=redis_url, key_builder=key_builder)
    event_isolation = storage.create_isolation()
    dp = Dispatcher(
        key_builder=None,  # because use custom FSM
        storage=None,  # because use custom FSM
        events_isolation=None,  # because use custom FSM
        disable_fsm=True,  # because use custom FSM
        user_repo=user_repo,
    )
    dp.update.outer_middleware(CurrentUserMiddleware())
    dp.update.outer_middleware(
        SharedFSMContextMiddleware(storage=storage, events_isolation=event_isolation),
    )
    dp.include_router(router)

    bot = Bot(token=token)

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    asyncio.run(main())
