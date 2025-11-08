from logging import getLogger
from typing import Optional, Union

from maxo import Bot
from maxo.enums import AttachmentType
from maxo.errors import MaxBotApiError, MaxBotBadRequestError
from maxo.tools.helpers import attachment_to_request
from maxo.tools.upload_media import FSInputFile, InputFile
from maxo.types import (
    Callback,
    # InputMediaAnimation,
    # InputMediaAudio,
    # InputMediaDocument,
    # InputMediaPhoto,
    # InputMediaVideo,
    Message,
    # ReplyKeyboardMarkup,
    # ReplyKeyboardRemove,
    # URLInputFile,
)
from maxo_dialog.api.entities import (
    MediaAttachment,
    NewMessage,
    OldMessage,
    ShowMode,
)
from maxo_dialog.api.protocols import (
    MessageManagerProtocol,
    MessageNotModified,
)

logger = getLogger(__name__)

SEND_METHODS = {
    AttachmentType.AUDIO: "send_audio",
    AttachmentType.IMAGE: "send_photo",
    AttachmentType.VIDEO: "send_video",
    AttachmentType.STICKER: "send_sticker",
    AttachmentType.VOICE: "send_voice",
}

INPUT_MEDIA_TYPES = {}

_INVALID_QUERY_ID_MSG = (
    "query is too old and response timeout expired or query id is invalid"
)


def _combine(sent_message: NewMessage, message_result: Message) -> OldMessage:
    return OldMessage(
        message_id=message_result.unsafe_body.mid,
        sequence_id=message_result.unsafe_body.seq,
        recipient=message_result.recipient,
        text=message_result.unsafe_body.text,
        attachments=message_result.unsafe_body.attachments or [],
    )


class MessageManager(MessageManagerProtocol):
    async def answer_callback(
        self,
        bot: Bot,
        callback: Callback,
    ) -> None:
        try:
            await bot.callback_answer(
                callback_id=callback.callback_id,
                notification="",
            )
        except MaxBotApiError as e:
            if _INVALID_QUERY_ID_MSG in e.message.lower():
                logger.warning("Cannot answer callback: %s", e)
            else:
                raise

    async def get_media_source(
        self,
        media: MediaAttachment,
        bot: Bot,
    ) -> Union[InputFile, str]:
        if media.file_id:
            return media.file_id.file_id
        if media.url:
            if media.use_pipe:
                return URLInputFile(media.url, bot=bot)
            return media.url
        else:
            return FSInputFile(media.path)

    def had_media(self, old_message: OldMessage) -> bool:
        return old_message.media_id is not None

    def need_media(self, new_message: NewMessage) -> bool:
        return bool(new_message.media)

    def need_reply_keyboard(self, new_message: Optional[NewMessage]) -> bool:
        if not new_message:
            return False
        return isinstance(new_message.reply_markup, ReplyKeyboardMarkup)

    def had_voice(self, old_message: OldMessage) -> bool:
        return old_message.content_type == AttachmentType.VOICE

    def need_voice(self, new_message: NewMessage) -> bool:
        return (
            new_message.media is not None
            and new_message.media.type == AttachmentType.VOICE
        )

    def _message_changed(
        self,
        new_message: NewMessage,
        old_message: OldMessage,
    ) -> bool:
        if (
            (new_message.text != old_message.text)
            or (new_message.keyboard)
            or
            # we do not know if link preview changed
            new_message.link_preview_options
        ):
            return True

        if self.had_media(old_message) != self.need_media(new_message):
            return True
        if not self.need_media(new_message):
            return False
        return False

    def _can_edit(self, new_message: NewMessage, old_message: OldMessage) -> bool:
        return True

    async def show_message(
        self,
        bot: Bot,
        new_message: NewMessage,
        old_message: Optional[OldMessage],
    ) -> OldMessage:
        if new_message.show_mode is ShowMode.NO_UPDATE:
            logger.debug("ShowMode is NO_UPDATE, skipping show")
            raise MessageNotModified("ShowMode is NO_UPDATE")
        if old_message and new_message.show_mode is ShowMode.DELETE_AND_SEND:
            logger.debug(
                "Delete and send new message, because: mode=%s",
                new_message.show_mode,
            )
            await self.remove_message_safe(bot, old_message, new_message)
            sent_message = await self.send_message(bot, new_message)
            return _combine(new_message, sent_message)
        if not old_message or new_message.show_mode is ShowMode.SEND:
            logger.debug(
                "Send new message, because: mode=%s, has old_message=%s",
                new_message.show_mode,
                bool(old_message),
            )
            await self._remove_kbd(bot, old_message, new_message)
            return _combine(
                new_message,
                await self.send_message(bot, new_message),
            )

        if not self._message_changed(new_message, old_message):
            logger.debug("Message dit not change")
            # nothing changed: text, keyboard or media
            return old_message

        if not self._can_edit(new_message, old_message):
            await self.remove_message_safe(bot, old_message, new_message)
            return _combine(
                new_message,
                await self.send_message(bot, new_message),
            )
        return _combine(
            new_message,
            await self.edit_message_safe(bot, new_message, old_message),
        )

    # Clear
    async def remove_kbd(
        self,
        bot: Bot,
        show_mode: ShowMode,
        old_message: Optional[OldMessage],
    ) -> bool:
        if show_mode is ShowMode.NO_UPDATE:
            return False
        if show_mode is ShowMode.DELETE_AND_SEND and old_message:
            return await self.remove_message_safe(bot, old_message, None)
        return await self._remove_kbd(bot, old_message, None)

    async def _remove_kbd(
        self,
        bot: Bot,
        old_message: Optional[OldMessage],
        new_message: Optional[NewMessage],
    ) -> bool:
        return await self.remove_inline_kbd(bot, old_message)

    async def remove_inline_kbd(
        self,
        bot: Bot,
        old_message: Optional[OldMessage],
    ) -> bool:
        if not old_message:
            return None
        logger.debug("remove_inline_kbd in %s", old_message.recipient)
        try:
            new_attachments = [
                attachment_to_request(attach)
                for attach in old_message.attachments
                if attach.type != AttachmentType.INLINE_KEYBOARD
            ]
            return (
                await bot.edit_message(
                    message_id=old_message.message_id,
                    attachments=new_attachments,
                )
            ).success
        except MaxBotBadRequestError as err:
            if "message is not modified" in err.message:
                pass  # nothing to remove
            elif (
                "message can't be edited" in err.message
                or "message to edit not found" in err.message
                or "MESSAGE_ID_INVALID" in err.message
            ):
                pass
            else:
                raise err

    async def remove_message_safe(
        self,
        bot: Bot,
        old_message: OldMessage,
        new_message: Optional[NewMessage],
    ) -> bool:
        try:
            await bot.delete_message(
                chat_id=old_message.recipient.chat_id,
                message_id=old_message.message_id,
            )
            return True
        except MaxBotBadRequestError as err:
            if "message to delete not found" in err.message:
                pass
            elif "message can't be deleted" in err.message:
                await self._remove_kbd(bot, old_message, new_message)
            else:
                raise

        return False

    async def edit_message_safe(
        self,
        bot: Bot,
        new_message: NewMessage,
        old_message: OldMessage,
    ) -> Message:
        try:
            return await self.edit_message(bot, new_message, old_message)
        except MaxBotBadRequestError as err:
            if "message is not modified" in err.message:
                raise MessageNotModified from err
            if (
                "message can't be edited" in err.message
                or "message to edit not found" in err.message
            ):
                return await self.send_message(bot, new_message)
            else:
                raise

    async def edit_message(
        self,
        bot: Bot,
        new_message: NewMessage,
        old_message: OldMessage,
    ) -> Message:
        # TODO: Отправка медиа в несколько шагов
        await bot.edit_message(
            link=new_message.link_to,
            message_id=old_message.message_id,
            text=new_message.text,
            attachments=new_message.attachments,
            format=new_message.parse_mode,
        )
        return await bot.get_message(message_id=old_message.message_id)

    async def send_message(self, bot: Bot, new_message: NewMessage) -> Message:
        # TODO: Отправка медиа в несколько шагов
        result = await bot.send_message(
            chat_id=new_message.recipient.chat_id,
            user_id=new_message.recipient.user_id,
            text=new_message.text,
            link=new_message.link_to,
            notify=True,
            attachments=new_message.attachments,
            format=new_message.parse_mode,
            disable_link_preview=False,  # FIXME
        )
        return result.message
