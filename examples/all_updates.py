import logging
import os

from maxo import Bot, Dispatcher
from maxo.routing.updates import (
    BotAddedToChat,
    BotRemovedFromChat,
    BotStarted,
    BotStopped,
    ChatTitleChanged,
    DialogCleared,
    DialogMuted,
    DialogRemoved,
    DialogUnmuted,
    MessageCallback,
    MessageCreated,
    MessageEdited,
    MessageRemoved,
    UserAddedToChat,
    UserRemovedFromChat,
)
from maxo.utils.facades import (
    BotAddedToChatFacade,
    BotRemovedFromChatFacade,
    BotStartedFacade,
    BotStoppedFacade,
    ChatTitleChangedFacade,
    DialogClearedFacade,
    DialogMutedFacade,
    DialogRemovedFacade,
    DialogUnmutedFacade,
    MessageCallbackFacade,
    MessageCreatedFacade,
    MessageEditedFacade,
    MessageRemovedFacade,
    UserAddedToChatFacade,
    UserRemovedFromChatFacade,
)
from maxo.utils.long_polling import LongPolling

logger = logging.getLogger(__name__)

bot = Bot(token=os.environ["TOKEN"])
dp = Dispatcher()


# Пример обработки всех типов апдейтов: сообщения, колбэки, события чата/бота
@dp.message_created()
async def message_created_handler(
    message_created: MessageCreated,
    facade: MessageCreatedFacade,
) -> None:
    await facade.reply_text(
        f"Привет! Я получил твое сообщение: '{message_created.message.body.text}'",
    )


@dp.message_edited()
async def message_edited_handler(
    message_edited: MessageEdited,
    facade: MessageEditedFacade,
) -> None:
    await facade.send_message(
        "Я заметил, что ты отредактировал сообщение "
        f"(ID: {message_edited.message.body.mid})\n"
        f"Новый текст: '{message_edited.message.body.text}'",
    )


@dp.message_callback()
async def message_callback_handler(
    message_callback: MessageCallback,
    facade: MessageCallbackFacade,
) -> None:
    await facade.callback_answer(notification="Ты нажал кнопку!")
    await facade.answer_text(
        f"Данные колбэка "
        f"(ID: {message_callback.callback.callback_id}, "
        f"сообщение ID: {message_callback.unsafe_message.body.mid}): "
        f"{message_callback.callback.payload}",
    )


@dp.message_removed()
async def message_removed_handler(
    message_removed: MessageRemoved,
    facade: MessageRemovedFacade,
) -> None:
    await facade.send_message(
        f"Сообщение (ID: {message_removed.message_id}) "
        f"было удалено из чата (ID: {message_removed.chat_id})",
    )


@dp.bot_started()
async def bot_started_handler(
    bot_started: BotStarted,
    facade: BotStartedFacade,
) -> None:
    bot_info = await facade.get_my_info()
    await facade.send_message(
        f"Привет! Я {bot_info.first_name}. Спасибо, что запустил меня!",
    )


@dp.bot_stopped()
async def bot_stopped_handler(
    bot_stopped: BotStopped,
    facade: BotStoppedFacade,
) -> None:
    logger.info(
        "Пользователь (ID: %s) остановил бота в чате (ID: %s)",
        facade.user.user_id,
        facade.chat_id,
    )


@dp.bot_added_to_chat()
async def bot_added_to_chat_handler(
    bot_added: BotAddedToChat,
    facade: BotAddedToChatFacade,
) -> None:
    await facade.send_message(
        f"Всем привет! Я новый бот в чате (ID: {facade.chat_id}), "
        f"меня добавил пользователь (ID: {facade.user.user_id})",
    )
    members = await facade.get_members()
    await facade.send_message(f"Я вижу здесь {len(members.members)} участников")


@dp.bot_removed_from_chat()
async def bot_removed_from_chat_handler(
    bot_removed: BotRemovedFromChat,
    facade: BotRemovedFromChatFacade,
) -> None:
    logger.info(
        "Бот был удален из чата (ID: %s) пользователем (ID: %s)",
        facade.chat_id,
        facade.user.user_id,
    )


@dp.user_added_to_chat()
async def user_added_to_chat_handler(
    user_added: UserAddedToChat,
    facade: UserAddedToChatFacade,
) -> None:
    await facade.send_message(
        f"Добро пожаловать в чат, {user_added.user.first_name} "
        f"(ID: {user_added.user.user_id})! "
        f"Я успешно обработал добавление нового пользователя",
    )


@dp.user_removed_from_chat()
async def user_removed_from_chat_handler(
    user_removed: UserRemovedFromChat,
    facade: UserRemovedFromChatFacade,
) -> None:
    await facade.send_message(
        f"Пользователь {user_removed.user.first_name} "
        f"(ID: {user_removed.user.user_id}) покинул чат (ID: {facade.chat_id})",
    )


@dp.chat_title_changed()
async def chat_title_changed_handler(
    chat_title_changed: ChatTitleChanged,
    facade: ChatTitleChangedFacade,
) -> None:
    await facade.send_message(
        f"Название чата (ID: {facade.chat_id}) "
        f"было изменено на '{chat_title_changed.title}' "
        f"пользователем (ID: {facade.user.user_id})",
    )


@dp.dialog_cleared()
async def dialog_cleared_handler(
    dialog_cleared: DialogCleared,
    facade: DialogClearedFacade,
) -> None:
    await facade.send_message(
        f"Диалог с пользователем (ID: {facade.user.user_id}) в чате "
        f"(ID: {facade.chat_id}) был очищен",
    )


@dp.dialog_muted()
async def dialog_muted_handler(
    dialog_muted: DialogMuted,
    facade: DialogMutedFacade,
) -> None:
    await facade.send_message(
        f"Диалог с пользователем (ID: {facade.user.user_id}) в чате "
        f"(ID: {facade.chat_id}) заглушен до {facade.muted_until}",
    )


@dp.dialog_removed()
async def dialog_removed_handler(
    dialog_removed: DialogRemoved,
    facade: DialogRemovedFacade,
) -> None:
    logger.info(
        "Диалог с пользователем (ID: %s) был удален из чата (ID: %s)",
        facade.user.user_id,
        facade.chat_id,
    )


@dp.dialog_unmuted()
async def dialog_unmuted_handler(
    dialog_unmuted: DialogUnmuted,
    facade: DialogUnmutedFacade,
) -> None:
    await facade.send_message(
        f"Диалог с пользователем (ID: {facade.user.user_id}) в чате "
        f"(ID: {facade.chat_id}) был разглушен",
    )


def main() -> None:
    logging.basicConfig(level=logging.DEBUG)
    LongPolling(dp).run(bot)


if __name__ == "__main__":
    main()
