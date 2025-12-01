import uuid
from datetime import datetime
from typing import Union

from maxo import Bot, Dispatcher
from maxo.bot.state import InitialBotState
from maxo.enums import ChatStatusType, ChatType, MessageLinkType
from maxo.routing.signals import Update
from maxo.routing.updates import MessageCallback, MessageCreated
from maxo.types import (
    BotInfo,
    Callback,
    CallbackKeyboardButton,
    Chat,
    LinkedMessage,
    Message,
    MessageBody,
    MessageStat,
    Recipient,
    User,
)

from .keyboard import InlineButtonLocator


class FakeBot(Bot):
    def __init__(self):
        super().__init__("", None, False)
        info = BotInfo(
            user_id=1,
            first_name="bot",
            username="bot",
            is_bot=True,
            last_activity_time=datetime.fromtimestamp(1234567890),
        )
        self._state = InitialBotState(info=info, api_client=None)

    def __hash__(self) -> int:
        return 1

    def __eq__(self, other: object) -> bool:
        return self is other


ChatMember = Union[
    None,
    # ChatMemberOwner,
    # ChatMemberAdministrator,
    # ChatMemberMember,
    # ChatMemberRestricted,
    # ChatMemberLeft,
    # ChatMemberBanned,
]


class BotClient:
    def __init__(
        self,
        dp: Dispatcher,
        user_id: int = 1,
        chat_id: int = 1,
        chat_type: ChatType = ChatType.DIALOG,
        bot: Bot | None = None,
    ):
        self.chat = Chat(
            chat_id=chat_id,
            type=chat_type,
            status=ChatStatusType.ACTIVE,
            last_event_time=datetime.now(),
            is_public=False,
            participants_count=2,
        )
        self.user = User(
            user_id=user_id,
            is_bot=False,
            first_name=f"User_{user_id}",
            last_activity_time=datetime.now(),
        )
        self.dp = dp
        self.last_update_id = 1
        self.last_message_id = 1
        self.bot = bot or FakeBot()

    def _new_update_id(self):
        self.last_update_id += 1
        return self.last_update_id

    def _new_message_id(self):
        self.last_message_id += 1
        return self.last_message_id

    def _new_message(
        self,
        text: str,
        reply_to: Message | None,
    ):
        message_seq = self._new_message_id()
        return Message(
            sender=self.user,
            recipient=Recipient(
                chat_type=ChatType.DIALOG,
                user_id=self.bot.state.info.user_id,
                chat_id=self.chat.chat_id,
            ),
            timestamp=datetime.fromtimestamp(1234567890),
            link=(
                LinkedMessage(
                    type=MessageLinkType.REPLY,
                    sender=reply_to.sender,
                    chat_id=reply_to.recipient.chat_id,
                    message=reply_to.unsafe_body,
                )
                if reply_to
                else None
            ),
            body=MessageBody(
                mid=str(message_seq),
                seq=message_seq,
                text=text,
            ),
            stat=MessageStat(
                views=1,
            ),
            url="https://max.ru/",
        )

    async def send(self, text: str, reply_to: Message | None = None):
        return await self.dp.feed_max_update(
            Update(
                update=MessageCreated(
                    message=self._new_message(text, reply_to),
                    timestamp=datetime.fromtimestamp(1234567890),
                    user_locale="ru",
                ),
            ),
            self.bot,
        )

    def _new_callback(
        self,
        button: CallbackKeyboardButton,
    ) -> Callback:
        if not button.payload:
            raise ValueError("Button has no callback data")
        return Callback(
            timestamp=datetime.fromtimestamp(1234567890),
            callback_id=str(uuid.uuid4()),
            payload=button.payload,
            user=self.user,
        )

    async def click(
        self,
        message: Message,
        locator: InlineButtonLocator,
    ) -> str:
        button = locator.find_button(message)
        if not button:
            raise ValueError(
                f"No button matching {locator} found",
            )

        callback = self._new_callback(button)
        await self.dp.feed_update(
            MessageCallback(
                timestamp=datetime.fromtimestamp(1234567890),
                callback=callback,
                message=message,
                user_locale="ru",
            ),
            self.bot,
        )
        return callback.callback_id
