import logging
import os

from maxo import Bot, Dispatcher
from maxo.routing.updates import MessageCreated
from maxo.utils.facades import MessageCreatedFacade
from maxo.utils.long_polling import LongPolling

bot = Bot(os.environ["TOKEN"])
dp = Dispatcher()


# Без фильтра - хендлер получает любое сообщение
@dp.message_created()
async def echo_handler(
    update: MessageCreated,
    facade: MessageCreatedFacade,
) -> None:
    text = update.message.body.text or "Текста нет"
    await facade.answer_text(text)


def main() -> None:
    logging.basicConfig(level=logging.DEBUG)
    LongPolling(dp).run(bot)


if __name__ == "__main__":
    main()
