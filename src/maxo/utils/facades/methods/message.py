from abc import ABC, abstractmethod
from collections.abc import Sequence

from maxo.enums import MessageLinkType, TextFormat
from maxo.omit import Omittable, Omitted
from maxo.types.buttons import InlineButtons
from maxo.types.chat import Chat
from maxo.types.chat_members_list import ChatMembersList
from maxo.types.message import Message
from maxo.types.new_message_link import NewMessageLink
from maxo.types.simple_query_result import SimpleQueryResult
from maxo.utils.facades.methods.attachments import AttachmentsFacade
from maxo.utils.helpers.calculating import calculate_chat_id_and_user_id
from maxo.utils.upload_media import InputFile


class MessageMethodsFacade(AttachmentsFacade, ABC):
    @property
    @abstractmethod
    def message(self) -> Message:
        raise NotImplementedError

    @property
    def chat_id(self) -> int:
        return self.message.recipient.chat_id

    async def delete_message(self) -> SimpleQueryResult:
        message_id = self.message.unsafe_body.mid
        return await self.bot.delete_message(message_id=message_id)

    async def send_message(
        self,
        text: str | None = None,
        link: NewMessageLink | None = None,
        notify: Omittable[bool] = True,
        format: TextFormat | None = None,
        disable_link_preview: Omittable[bool] = Omitted(),
        keyboard: Sequence[Sequence[InlineButtons]] | None = None,
        media: Sequence[InputFile] | None = None,
    ) -> Message:
        recipient = self.message.recipient
        chat_id, user_id = calculate_chat_id_and_user_id(
            chat_id=recipient.chat_id,
            user_id=recipient.user_id,
            chat_type=recipient.chat_type,
        )

        attachments = await self._build_attachments(
            base=[],
            keyboard=keyboard,
            media=media,
        )

        result = await self.bot.send_message(
            chat_id=chat_id or Omitted(),
            user_id=user_id or Omitted(),
            text=text,
            attachments=attachments,
            link=link,
            notify=notify,
            format=format,
            disable_link_preview=disable_link_preview,
        )
        return result.message

    async def answer_text(
        self,
        text: str,
        keyboard: Sequence[Sequence[InlineButtons]] | None = None,
        notify: Omittable[bool] = True,
        format: TextFormat | None = None,
        disable_link_preview: Omittable[bool] = Omitted(),
    ) -> Message:
        return await self.send_message(
            text=text,
            notify=notify,
            format=format,
            keyboard=keyboard,
            disable_link_preview=disable_link_preview,
        )

    async def reply_text(
        self,
        text: str,
        keyboard: Sequence[Sequence[InlineButtons]] | None = None,
        notify: Omittable[bool] = True,
        format: TextFormat | None = None,
        disable_link_preview: Omittable[bool] = Omitted(),
    ) -> Message:
        return await self.send_message(
            text=text,
            notify=notify,
            format=format,
            keyboard=keyboard,
            disable_link_preview=disable_link_preview,
            link=self._make_new_message_link(MessageLinkType.REPLY),
        )

    async def send_media(
        self,
        media: InputFile | Sequence[InputFile],
        text: str | None = None,
        keyboard: Sequence[Sequence[InlineButtons]] | None = None,
        notify: Omittable[bool] = True,
        format: TextFormat | None = None,
        link: NewMessageLink | None = None,
        disable_link_preview: Omittable[bool] = Omitted(),
    ) -> Message:
        if isinstance(media, InputFile):
            media = (media,)

        return await self.send_message(
            text=text,
            media=media,
            notify=notify,
            format=format,
            keyboard=keyboard,
            disable_link_preview=disable_link_preview,
            link=link,
        )

    async def edit_message(
        self,
        text: str | None = None,
        keyboard: Sequence[Sequence[InlineButtons]] | None = None,
        media: Sequence[InputFile] | None = None,
        link: NewMessageLink | None = None,
        notify: bool = True,
        format: TextFormat | None = None,
    ) -> Message:
        message_id = self.message.unsafe_body.mid

        if text is None:
            text = self.message.unsafe_body.text

        attachments = await self._build_attachments(
            base=[],
            keyboard=keyboard,
            media=media,
        )

        return await self.bot.edit_message(
            message_id=message_id,
            text=text,
            attachments=attachments,
            link=link,
            notify=notify,
            format=format,
        )

    def _make_new_message_link(self, type: MessageLinkType) -> NewMessageLink:
        return NewMessageLink(
            type=type,
            mid=self.message.unsafe_body.mid,
        )

    async def get_chat(self) -> Chat:
        return await self.bot.get_chat(chat_id=self.chat_id)

    async def get_members(
        self,
        count: Omittable[int] = Omitted(),
        marker: Omittable[int] = Omitted(),
        user_ids: Omittable[list[int] | None] = Omitted(),
    ) -> ChatMembersList:
        return await self.bot.get_members(
            chat_id=self.chat_id,
            count=count,
            marker=marker,
            user_ids=user_ids,
        )

    async def leave_chat(self) -> SimpleQueryResult:
        return await self.bot.leave_chat(chat_id=self.chat_id)

    async def get_message_by_id(self, message_id: str) -> Message:
        return await self.bot.get_message_by_id(message_id=message_id)
