import logging
import os
from typing import Any

from magic_filter import F

from maxo import Bot, Dispatcher
from maxo.fsm import FSMContext, State, StateFilter, StatesGroup
from maxo.integrations.magic_filter import MagicFilter
from maxo.routing.filters import AndFilter, CommandStart
from maxo.routing.updates import MessageCreated
from maxo.types import MessageButton
from maxo.utils.builders import KeyboardBuilder
from maxo.utils.facades import MessageCreatedFacade
from maxo.utils.long_polling import LongPolling

logger = logging.getLogger(__name__)

dp = Dispatcher()


# FSM: состояния и переходы между ними, данные в fsm_context
class Form(StatesGroup):
    name = State()
    like_bots = State()
    language = State()


@dp.message_created(CommandStart())
async def command_start(
    message: MessageCreated,
    facade: MessageCreatedFacade,
    fsm_context: FSMContext,
) -> None:
    await fsm_context.set_state(Form.name)
    await facade.answer_text("Привет! Как тебя зовут?")


@dp.message_created(MagicFilter(F.text.casefold() == "отмена"))
async def cancel_handler(
    message: MessageCreated,
    facade: MessageCreatedFacade,
    fsm_context: FSMContext,
) -> None:
    current_state = await fsm_context.get_state()
    if current_state is None:
        return

    logger.info("Cancelling state %r", current_state)
    await fsm_context.clear()
    await facade.answer_text("Отменено.")


@dp.message_created(StateFilter(Form.name))
async def process_name(
    message: MessageCreated,
    facade: MessageCreatedFacade,
    fsm_context: FSMContext,
) -> None:
    await fsm_context.update_data(name=message.message.body.text)
    await fsm_context.set_state(Form.like_bots)
    await facade.answer_text(
        f"Приятно, {message.message.body.text}!\nНравится писать ботов?",
        keyboard=KeyboardBuilder()
        .add(
            MessageButton(text="Да"),
            MessageButton(text="Нет"),
        )
        .build(),
    )


@dp.message_created(
    AndFilter(
        StateFilter(Form.like_bots),
        MagicFilter(F.text.casefold() == "нет"),
    ),
)
async def process_dont_like_write_bots(
    message: MessageCreated,
    facade: MessageCreatedFacade,
    fsm_context: FSMContext,
) -> None:
    data = await fsm_context.get_data()
    await fsm_context.clear()
    await facade.answer_text("Ну ладно.\nДо встречи.")
    await show_summary(facade=facade, data=data, positive=False)


@dp.message_created(
    AndFilter(
        StateFilter(Form.like_bots),
        MagicFilter(F.text.casefold() == "да"),
    ),
)
async def process_like_write_bots(
    message: MessageCreated,
    facade: MessageCreatedFacade,
    fsm_context: FSMContext,
) -> None:
    await fsm_context.set_state(Form.language)
    await facade.reply_text(
        "Круто! Я тоже!\nНа каком языке программировал?",
    )


@dp.message_created(StateFilter(Form.like_bots))
async def process_unknown_write_bots(
    message: MessageCreated,
    facade: MessageCreatedFacade,
) -> None:
    await facade.reply_text("Не понял :(")


@dp.message_created(StateFilter(Form.language))
async def process_language(
    message: MessageCreated,
    facade: MessageCreatedFacade,
    fsm_context: FSMContext,
) -> None:
    data = await fsm_context.update_data(language=message.message.body.text)
    await fsm_context.clear()

    if message.message.body.text and message.message.body.text.casefold() == "python":
        await facade.reply_text(
            "Python? Это тот язык, от которого у меня загораются схемы! 😉",
        )

    await show_summary(facade=facade, data=data)


async def show_summary(
    facade: MessageCreatedFacade,
    data: dict[str, Any],
    positive: bool = True,
) -> None:
    name = data["name"]
    language = data.get("language", "<не указано>")
    text = f"Запомню: {name}, "
    text += (
        f"тебе нравится писать ботов на {language}."
        if positive
        else "тебе не нравится писать ботов, жаль..."
    )
    await facade.answer_text(text=text)


def main() -> None:
    logging.basicConfig(level=logging.DEBUG)
    bot = Bot(token=os.environ["TOKEN"])
    LongPolling(dp).run(bot)


if __name__ == "__main__":
    main()
