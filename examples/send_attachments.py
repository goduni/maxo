import logging
import os

from maxo import Bot, Dispatcher
from maxo.routing.updates import MessageCreated
from maxo.utils.facades import MessageCreatedFacade
from maxo.utils.long_polling import LongPolling
from maxo.utils.upload_media import FSInputFile

dp = Dispatcher()


@dp.message_created()
async def attachments_handler(
    update: MessageCreated,
    facade: MessageCreatedFacade,
) -> None:
    # в одном сообщении API принимает только один файл — отправляем по одному
    for file in (
        FSInputFile.image(path="./files/watermelon.jpg"),
        FSInputFile.file(path="files/watermelon.txt"),
        FSInputFile.audio(path="./files/watermelon.mp3"),
        FSInputFile.video(path="./files/watermelon.mp4"),
    ):
        await facade.send_message(media=(file,))


def main() -> None:
    logging.basicConfig(level=logging.DEBUG)
    bot = Bot(token=os.environ["TOKEN"])
    LongPolling(dp).run(bot)


if __name__ == "__main__":
    main()
