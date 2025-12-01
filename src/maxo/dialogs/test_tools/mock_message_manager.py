from datetime import datetime
from uuid import uuid4

from maxo import Bot
from maxo.dialogs import ShowMode
from maxo.dialogs.api.entities import MediaAttachment, NewMessage, OldMessage
from maxo.dialogs.api.protocols import (
    MessageManagerProtocol,
    MessageNotModified,
)
from maxo.enums import ChatType
from maxo.types import (
    AudioAttachment,
    Callback,
    FileAttachment,
    Message,
    MessageBody,
    Recipient,
    VideoAttachment,
)


def file_id(media: MediaAttachment) -> str:
    file_id_ = None
    if media.file_id:
        file_id_ = media.file_id.file_id
    return file_id_ or str(uuid4())


def file_unique_id(media: MediaAttachment) -> str:
    file_unique_id_ = None
    if media.file_id:
        file_unique_id_ = media.file_id.file_unique_id
    return file_unique_id_ or str(uuid4())


MEDIA_CLASSES = {
    "audio": lambda x: AudioAttachment(
        file_id=file_id(x),
        file_unique_id=file_unique_id(x),
        duration=1024,
    ),
    "document": lambda x: FileAttachment(
        file_id=file_id(x),
        file_unique_id=file_unique_id(x),
    ),
    "photo": lambda x: [
        PhotoSize(
            file_id=file_id(x),
            file_unique_id=file_unique_id(x),
            width=1024,
            height=1024,
        ),
    ],
    "video": lambda x: VideoAttachment(
        file_id=file_id(x),
        file_unique_id=file_unique_id(x),
        width=1024,
        height=1024,
        duration=1024,
    ),
}


class MockMessageManager(MessageManagerProtocol):
    def __init__(self):
        self.answered_callbacks: set[str] = set()
        self.sent_messages = []
        self.last_message_id = 0

    def reset_history(self):
        self.sent_messages.clear()
        self.answered_callbacks.clear()

    def assert_one_message(self) -> None:
        assert len(self.sent_messages) == 1

    def last_message(self) -> Message:
        return self.sent_messages[-1]

    def first_message(self) -> Message:
        return self.sent_messages[0]

    def one_message(self) -> Message:
        self.assert_one_message()
        return self.first_message()

    async def remove_kbd(
        self,
        bot: Bot,
        show_mode: ShowMode,
        old_message: OldMessage | None,
    ) -> Message | None:
        if not old_message:
            return None
        if show_mode in (ShowMode.DELETE_AND_SEND, ShowMode.NO_UPDATE):
            return None
        assert isinstance(old_message, OldMessage)

        message = Message(
            timestamp=datetime.now(),
            recipient=Recipient(
                chat_type=ChatType.DIALOG,
                chat_id=old_message.recipient.chat_id,
                user_id=old_message.recipient.chat_id,
            ),
        )
        self.sent_messages.append(message)
        return message

    async def answer_callback(
        self,
        bot: Bot,
        callback: Callback,
    ) -> None:
        self.answered_callbacks.add(callback.callback_id)

    def assert_answered(self, callback_id: str) -> None:
        assert callback_id in self.answered_callbacks

    async def show_message(
        self,
        bot: Bot,
        new_message: NewMessage,
        old_message: OldMessage | None,
    ) -> OldMessage:
        assert isinstance(new_message, NewMessage)
        assert isinstance(old_message, (OldMessage, type(None)))
        if new_message.show_mode is ShowMode.NO_UPDATE:
            raise MessageNotModified

        message_id = self.last_message_id + 1
        self.last_message_id = message_id

        self.sent_messages.append(
            Message(
                sender=bot.state.info,
                recipient=new_message.recipient,
                timestamp=datetime.now(),
                body=MessageBody(
                    mid=str(message_id),
                    seq=message_id,
                    text=new_message.text,
                    attachments=new_message.attachments,
                ),
            ),
        )

        return OldMessage(
            message_id=str(message_id),
            sequence_id=message_id,
            recipient=new_message.recipient,
            text=new_message.text,
            attachments=new_message.attachments,
        )
