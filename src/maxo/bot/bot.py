import json
import pathlib
from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager
from typing import Any, BinaryIO, Self, TypeVar

from aiohttp import ClientSession
from unihttp.bind_method import bind_method
from unihttp.middlewares import AsyncMiddleware

from maxo.bot.api_client import MaxApiClient
from maxo.bot.methods import (
    AddMembers,
    AnswerOnCallback,
    DeleteAdmin,
    DeleteChat,
    DeleteMessage,
    EditBotInfo,
    EditChat,
    EditMessage,
    GetAdmins,
    GetChat,
    GetChatByLink,
    GetChats,
    GetMembers,
    GetMembership,
    GetMessageById,
    GetMessages,
    GetMyInfo,
    GetPinnedMessage,
    GetSubscriptions,
    GetUpdates,
    GetUploadUrl,
    GetVideoAttachmentDetails,
    LeaveChat,
    PinMessage,
    RemoveMember,
    SendAction,
    SendMessage,
    SetAdmins,
    Subscribe,
    UnpinMessage,
    Unsubscribe,
    UploadMedia,
)
from maxo.bot.methods.base import MaxoMethod
from maxo.bot.state import (
    BotState,
    ClosedBotState,
    ConnectingBotState,
    EmptyBotState,
    RunningBotState,
)
from maxo.enums.text_format import TextFormat
from maxo.types import AttachmentPayload, MaxoType

_MethodResultT = TypeVar("_MethodResultT", bound=MaxoType)


class Bot:
    __slots__ = (
        "_json_dumps",
        "_json_loads",
        "_middleware",
        "_session",
        "_state",
        "_text_format",
        "_token",
        "_warming_up",
    )

    def __init__(
        self,
        token: str,
        text_format: TextFormat | None = None,
        warming_up: bool = True,
        middleware: list[AsyncMiddleware] | None = None,
        session: ClientSession | None = None,
        json_dumps: Callable[[Any], str] = json.dumps,
        json_loads: Callable[[str | bytes | bytearray], Any] = json.loads,
    ) -> None:
        self._token = token
        self._text_format = text_format
        self._warming_up = warming_up
        self._middleware = middleware
        self._session = session
        self._json_dumps = json_dumps
        self._json_loads = json_loads

        self._state = EmptyBotState()

    @property
    def state(self) -> BotState:
        return self._state

    async def start(self) -> None:
        if self.state.started:
            return

        api_client = MaxApiClient(
            token=self._token,
            warming_up=self._warming_up,
            text_format=self._text_format,
            middleware=self._middleware,
            session=self._session,
            json_dumps=self._json_dumps,
            json_loads=self._json_loads,
        )
        self._state = ConnectingBotState(api_client=api_client)

        info = await self.get_my_info()
        self._state = RunningBotState(info=info, api_client=api_client)

    @asynccontextmanager
    async def context(self, auto_close: bool = True) -> AsyncIterator[Self]:
        try:
            await self.start()
            yield self
        finally:
            if auto_close:
                await self.close()

    async def call_method(
        self,
        method: MaxoMethod[_MethodResultT],
    ) -> _MethodResultT:
        return await self.state.api_client.call_method(method)

    async def close(self) -> None:
        if self.state.closed or not self.state.started:
            return

        await self.state.api_client.close()
        self._state = ClosedBotState()

    async def download(
        self,
        url: str | AttachmentPayload,
        destination: BinaryIO | pathlib.Path | str | None = None,
        timeout: int = 30,
        chunk_size: int = 65536,
        seek: bool = True,
    ) -> BinaryIO | None:
        return await self.state.api_client.download(
            url=url,
            destination=destination,
            timeout=timeout,
            chunk_size=chunk_size,
            seek=seek,
        )

    # Bots

    edit_bot_info = bind_method(EditBotInfo)
    get_my_info = bind_method(GetMyInfo)

    # Chats

    add_members = bind_method(AddMembers)
    delete_admin = bind_method(DeleteAdmin)
    delete_chat = bind_method(DeleteChat)
    edit_chat = bind_method(EditChat)
    get_admins = bind_method(GetAdmins)
    get_chat = bind_method(GetChat)
    get_chat_by_link = bind_method(GetChatByLink)
    get_chats = bind_method(GetChats)
    get_members = bind_method(GetMembers)
    get_membership = bind_method(GetMembership)
    get_pinned_message = bind_method(GetPinnedMessage)
    leave_chat = bind_method(LeaveChat)
    pin_message = bind_method(PinMessage)
    remove_member = bind_method(RemoveMember)
    send_action = bind_method(SendAction)
    set_admins = bind_method(SetAdmins)
    unpin_message = bind_method(UnpinMessage)

    # Messages

    answer_on_callback = bind_method(AnswerOnCallback)
    delete_message = bind_method(DeleteMessage)
    edit_message = bind_method(EditMessage)
    get_message_by_id = bind_method(GetMessageById)
    get_messages = bind_method(GetMessages)
    get_video_attachment_details = bind_method(GetVideoAttachmentDetails)
    send_message = bind_method(SendMessage)

    # Subscriptions

    get_subscriptions = bind_method(GetSubscriptions)
    get_updates = bind_method(GetUpdates)
    subscribe = bind_method(Subscribe)
    unsubscribe = bind_method(Unsubscribe)

    # Uploads

    get_upload_url = bind_method(GetUploadUrl)
    upload_media = bind_method(UploadMedia)
