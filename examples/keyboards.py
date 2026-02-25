import logging
import os

from magic_filter import F

from maxo import Bot, Ctx, Dispatcher, Router
from maxo.integrations.magic_filter import MagicFilter
from maxo.routing.filters import CommandStart
from maxo.routing.updates import MessageCallback, MessageCreated
from maxo.utils.builders import KeyboardBuilder
from maxo.utils.facades import MessageCallbackFacade, MessageCreatedFacade
from maxo.utils.long_polling import LongPolling

router = Router()


# KeyboardBuilder: callback, link, request_contact, request_geo_location;
# adjust — кол-во кнопок в ряд
@router.message_created(CommandStart())
async def start_handler(
    update: MessageCreated,
    ctx: Ctx,
    facade: MessageCreatedFacade,
) -> None:
    keyboard = (
        KeyboardBuilder()
        .add_callback(
            text="Кликни на меня",
            payload="click_me",
        )
        .add_link(text="Ссылка на google", url="https://google.com")
        .add_request_contact(text="Поделится контактами")
        .add_request_geo_location(text="Поделится гео позицией")
        .adjust(3)
    )

    await facade.answer_text(
        "Клавиатура",
        keyboard=keyboard.build(),
    )


@router.message_callback(MagicFilter(F.payload == "click_me"))
async def click_me_handler(
    update: MessageCallback,
    facade: MessageCallbackFacade,
) -> None:
    await facade.callback_answer("Ты кликнул на меня")


def main() -> None:
    logging.basicConfig(level=logging.DEBUG)

    bot = Bot(os.environ["TOKEN"])
    dp = Dispatcher()
    dp.include(router)

    LongPolling(dp).run(bot)


if __name__ == "__main__":
    main()
