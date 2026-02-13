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

bot = Bot(token=os.environ["TOKEN"])
dispatcher = Dispatcher()


@dispatcher.message_created()
async def message_created_handler(
    update: MessageCreated,
    facade: MessageCreatedFacade,
) -> None:
    await facade.reply_text(
        f"Привет! Я получил твое сообщение: '{update.message.unsafe_body.text}'",
    )


@dispatcher.message_edited()
async def message_edited_handler(
    update: MessageEdited,
    facade: MessageEditedFacade,
) -> None:
    await facade.send_message(
        text=f"Я заметил, что ты отредактировал сообщение (ID: {update.message.unsafe_body.mid})\n"
        f"Новый текст: '{update.message.unsafe_body.text}'",
    )


@dispatcher.message_callback()
async def message_callback_handler(
    update: MessageCallback,
    facade: MessageCallbackFacade,
) -> None:
    await facade.callback_answer(notification="Ты нажал кнопку!")
    await facade.answer_text(
        f"Данные колбэка "
        f"(ID: {update.callback.callback_id}, сообщение ID: {update.message.unsafe_body.mid}): "
        f"{update.callback.payload}",
    )


@dispatcher.message_removed()
async def message_removed_handler(
    update: MessageRemoved,
    facade: MessageRemovedFacade,
) -> None:
    await facade.send_message(
        f"Сообщение (ID: {update.message_id}) "
        f"было удалено из чата (ID: {update.chat_id})",
    )


@dispatcher.bot_started()
async def bot_started_handler(
    update: BotStarted,
    facade: BotStartedFacade,
) -> None:
    bot_info = await facade.get_my_info()
    await facade.send_message(
        f"Привет! Я {bot_info.first_name}. Спасибо, что запустил меня!",
    )


@dispatcher.bot_stopped()
async def bot_stopped_handler(
    update: BotStopped,
    facade: BotStoppedFacade,
) -> None:
    logging.info(
        "Пользователь (ID: %s) остановил бота в чате (ID: %s)",
        facade.user.user_id,
        facade.chat_id,
    )


@dispatcher.bot_added_to_chat()
async def bot_added_to_chat_handler(
    update: BotAddedToChat,
    facade: BotAddedToChatFacade,
) -> None:
    await facade.send_message(
        f"Всем привет! Я новый бот в чате (ID: {facade.chat_id}), "
        f"меня добавил пользователь (ID: {facade.user.user_id})",
    )
    members = await facade.get_members()
    await facade.send_message(f"Я вижу здесь {len(members.members)} участников")


@dispatcher.bot_removed_from_chat()
async def bot_removed_from_chat_handler(
    update: BotRemovedFromChat,
    facade: BotRemovedFromChatFacade,
) -> None:
    logging.info(
        "Бот был удален из чата (ID: %s) пользователем (ID: %s)",
        facade.chat_id,
        facade.user.user_id,
    )


@dispatcher.user_added_to_chat()
async def user_added_to_chat_handler(
    update: UserAddedToChat,
    facade: UserAddedToChatFacade,
) -> None:
    await facade.send_message(
        f"Добро пожаловать в чат, {update.user.first_name} (ID: {update.user.user_id})! "
        f"Я успешно обработал добавление нового пользователя",
    )


@dispatcher.user_removed_from_chat()
async def user_removed_from_chat_handler(
    update: UserRemovedFromChat,
    facade: UserRemovedFromChatFacade,
) -> None:
    await facade.send_message(
        f"Пользователь {update.user.first_name} (ID: {update.user.user_id}) покинул чат (ID: {facade.chat_id})",
    )


@dispatcher.chat_title_changed()
async def chat_title_changed_handler(
    update: ChatTitleChanged,
    facade: ChatTitleChangedFacade,
) -> None:
    await facade.send_message(
        f"Название чата (ID: {facade.chat_id}) было изменено на '{update.title}' пользователем (ID: {facade.user.user_id})",
    )


@dispatcher.dialog_cleared()
async def dialog_cleared_handler(
    update: DialogCleared,
    facade: DialogClearedFacade,
) -> None:
    await facade.send_message(
        f"Диалог с пользователем (ID: {facade.user.user_id}) в чате (ID: {facade.chat_id}) был очищен",
    )


@dispatcher.dialog_muted()
async def dialog_muted_handler(
    update: DialogMuted,
    facade: DialogMutedFacade,
) -> None:
    await facade.send_message(
        f"Диалог с пользователем (ID: {facade.user.user_id}) в чате (ID: {facade.chat_id}) заглушен до {facade.muted_until}",
    )


@dispatcher.dialog_removed()
async def dialog_removed_handler(
    update: DialogRemoved,
    facade: DialogRemovedFacade,
) -> None:
    logging.info(
        "Диалог с пользователем (ID: %s) был удален из чата (ID: %s)",
        facade.user.user_id,
        facade.chat_id,
    )


@dispatcher.dialog_unmuted()
async def dialog_unmuted_handler(
    update: DialogUnmuted,
    facade: DialogUnmutedFacade,
) -> None:
    await facade.send_message(
        f"Диалог с пользователем (ID: {facade.user.user_id}) в чате (ID: {facade.chat_id}) был разглушен",
    )


logging.basicConfig(level=logging.DEBUG)
LongPolling(dispatcher).run(bot)
