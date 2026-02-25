import json
from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any, Never

from adaptix import Chain, P, Retort, dumper, loader
from aiohttp import ClientSession
from unihttp.clients.aiohttp import AiohttpAsyncClient
from unihttp.http import HTTPResponse
from unihttp.markers import QueryMarker
from unihttp.method import BaseMethod
from unihttp.middlewares import AsyncMiddleware
from unihttp.serializers.adaptix import DEFAULT_RETORT, for_marker

from maxo import loggers
from maxo.__meta__ import __version__
from maxo._internal._adaptix.concat_provider import concat_provider
from maxo._internal._adaptix.has_tag_provider import has_tag_provider
from maxo.bot.warming_up import WarmingUpType, warming_up_retort
from maxo.enums import (
    AttachmentRequestType,
    AttachmentType,
    ButtonType,
    MarkupElementType,
    UpdateType,
)
from maxo.enums.text_format import TextFormat
from maxo.errors import (
    MaxBotApiError,
    MaxBotBadRequestError,
    MaxBotForbiddenError,
    MaxBotMethodNotAllowedError,
    MaxBotNotFoundError,
    MaxBotServiceUnavailableError,
    MaxBotTooManyRequestsError,
    MaxBotUnauthorizedError,
    MaxBotUnknownServerError,
)
from maxo.omit import Omittable
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
from maxo.types import (
    Attachments,
    AudioAttachment,
    AudioAttachmentRequest,
    CallbackButton,
    ContactAttachment,
    ContactAttachmentRequest,
    EmphasizedMarkup,
    FileAttachment,
    FileAttachmentRequest,
    InlineKeyboardAttachment,
    InlineKeyboardAttachmentRequest,
    LinkButton,
    LinkMarkup,
    LocationAttachment,
    LocationAttachmentRequest,
    MessageButton,
    MonospacedMarkup,
    OpenAppButton,
    PhotoAttachment,
    PhotoAttachmentRequest,
    RequestContactButton,
    RequestGeoLocationButton,
    ShareAttachment,
    ShareAttachmentRequest,
    StickerAttachment,
    StickerAttachmentRequest,
    StrikethroughMarkup,
    StrongMarkup,
    UnderlineMarkup,
    UserMentionMarkup,
    VideoAttachment,
    VideoAttachmentRequest,
)

_has_tag_providers = concat_provider(
    # ---> UpdateType <---
    has_tag_provider(BotAddedToChat, "update_type", UpdateType.BOT_ADDED),
    has_tag_provider(BotRemovedFromChat, "update_type", UpdateType.BOT_REMOVED),
    has_tag_provider(BotStarted, "update_type", UpdateType.BOT_STARTED),
    has_tag_provider(BotStopped, "update_type", UpdateType.BOT_STOPPED),
    has_tag_provider(ChatTitleChanged, "update_type", UpdateType.CHAT_TITLE_CHANGED),
    has_tag_provider(DialogCleared, "update_type", UpdateType.DIALOG_CLEARED),
    has_tag_provider(DialogMuted, "update_type", UpdateType.DIALOG_MUTED),
    has_tag_provider(DialogRemoved, "update_type", UpdateType.DIALOG_REMOVED),
    has_tag_provider(DialogUnmuted, "update_type", UpdateType.DIALOG_UNMUTED),
    has_tag_provider(MessageCallback, "update_type", UpdateType.MESSAGE_CALLBACK),
    has_tag_provider(MessageCreated, "update_type", UpdateType.MESSAGE_CREATED),
    has_tag_provider(MessageEdited, "update_type", UpdateType.MESSAGE_EDITED),
    has_tag_provider(MessageRemoved, "update_type", UpdateType.MESSAGE_REMOVED),
    has_tag_provider(UserAddedToChat, "update_type", UpdateType.USER_ADDED),
    has_tag_provider(UserRemovedFromChat, "update_type", UpdateType.USER_REMOVED),
    # ---> AttachmentType <---
    has_tag_provider(AudioAttachment, "type", AttachmentType.AUDIO),
    has_tag_provider(ContactAttachment, "type", AttachmentType.CONTACT),
    has_tag_provider(FileAttachment, "type", AttachmentType.FILE),
    has_tag_provider(PhotoAttachment, "type", AttachmentType.IMAGE),
    has_tag_provider(InlineKeyboardAttachment, "type", AttachmentType.INLINE_KEYBOARD),
    has_tag_provider(LocationAttachment, "type", AttachmentType.LOCATION),
    has_tag_provider(ShareAttachment, "type", AttachmentType.SHARE),
    has_tag_provider(StickerAttachment, "type", AttachmentType.STICKER),
    has_tag_provider(VideoAttachment, "type", AttachmentType.VIDEO),
    # ---> MarkupElementType <---
    has_tag_provider(EmphasizedMarkup, "type", MarkupElementType.EMPHASIZED),
    has_tag_provider(LinkMarkup, "type", MarkupElementType.LINK),
    has_tag_provider(MonospacedMarkup, "type", MarkupElementType.MONOSPACED),
    has_tag_provider(
        StrikethroughMarkup,
        "type",
        MarkupElementType.STRIKETHROUGH,
    ),
    has_tag_provider(StrongMarkup, "type", MarkupElementType.STRONG),
    has_tag_provider(UnderlineMarkup, "type", MarkupElementType.UNDERLINE),
    has_tag_provider(UserMentionMarkup, "type", MarkupElementType.USER_MENTION),
    # ---> AttachmentRequestType <---
    has_tag_provider(PhotoAttachmentRequest, "type", AttachmentRequestType.IMAGE),
    has_tag_provider(VideoAttachmentRequest, "type", AttachmentRequestType.VIDEO),
    has_tag_provider(AudioAttachmentRequest, "type", AttachmentRequestType.AUDIO),
    has_tag_provider(FileAttachmentRequest, "type", AttachmentRequestType.FILE),
    has_tag_provider(StickerAttachmentRequest, "type", AttachmentRequestType.STICKER),
    has_tag_provider(ContactAttachmentRequest, "type", AttachmentRequestType.CONTACT),
    has_tag_provider(
        InlineKeyboardAttachmentRequest,
        "type",
        AttachmentRequestType.INLINE_KEYBOARD,
    ),
    has_tag_provider(LocationAttachmentRequest, "type", AttachmentRequestType.LOCATION),
    has_tag_provider(ShareAttachmentRequest, "type", AttachmentRequestType.SHARE),
    # ---> KeyboardButtonType <---
    has_tag_provider(CallbackButton, "type", ButtonType.CALLBACK),
    has_tag_provider(LinkButton, "type", ButtonType.LINK),
    has_tag_provider(
        RequestContactButton,
        "type",
        ButtonType.REQUEST_CONTACT,
    ),
    has_tag_provider(
        RequestGeoLocationButton,
        "type",
        ButtonType.REQUEST_GEO_LOCATION,
    ),
    has_tag_provider(
        OpenAppButton,
        "type",
        ButtonType.OPEN_APP,
    ),
    has_tag_provider(
        MessageButton,
        "type",
        ButtonType.MESSAGE,
    ),
)


class MaxApiClient(AiohttpAsyncClient):
    def __init__(
        self,
        token: str,
        warming_up: bool,
        text_format: TextFormat | None = None,
        base_url: str = "https://platform-api.max.ru/",
        middleware: list[AsyncMiddleware] | None = None,
        session: ClientSession | None = None,
        json_dumps: Callable[[Any], str] = json.dumps,
        json_loads: Callable[[str | bytes | bytearray], Any] = json.loads,
    ) -> None:
        self._token = token
        self._warming_up = warming_up
        self._text_format = text_format

        if session is None:
            session = ClientSession()

        if "Authorization" not in session.headers:
            session.headers["Authorization"] = self._token
        if "User-Agent" not in session.headers:
            session.headers["User-Agent"] = f"maxo/{__version__}"

        if middleware is None:
            middleware = []

        request_dumper = self._init_method_dumper()
        response_loader = self._init_response_loader()

        super().__init__(
            base_url=base_url,
            request_dumper=request_dumper,
            response_loader=response_loader,
            middleware=middleware,
            session=session,
            json_dumps=json_dumps,
            json_loads=json_loads,
        )

    def _init_method_dumper(self) -> Retort:
        retort = DEFAULT_RETORT.extend(
            recipe=[
                _has_tag_providers,
                dumper(
                    for_marker(QueryMarker, P[None]),
                    lambda _: "null",
                ),
                dumper(
                    for_marker(QueryMarker, P[bool]),
                    lambda item: int(item),
                ),
                dumper(
                    for_marker(QueryMarker, P[list[str]] | P[list[int]]),
                    lambda seq: ",".join(str(el) for el in seq),
                ),
                dumper(
                    P[TextFormat]
                    | P[TextFormat | None]
                    | P[Omittable[TextFormat]]
                    | P[Omittable[TextFormat | None]],
                    lambda item: item or self._text_format,
                ),
                dumper(
                    P[Attachments],
                    lambda attachment: attachment.to_request(),
                    chain=Chain.FIRST,
                ),
            ],
        )

        if self._warming_up:
            retort = warming_up_retort(retort, warming_up=WarmingUpType.METHOD)

        return retort

    def _init_response_loader(self) -> Retort:
        retort = DEFAULT_RETORT.extend(
            recipe=[
                _has_tag_providers,
                loader(P[datetime], lambda x: datetime.fromtimestamp(x / 1000, tz=UTC)),
            ],
        )

        if self._warming_up:
            retort = warming_up_retort(retort, warming_up=WarmingUpType.TYPES)

        return retort

    def handle_error(self, response: HTTPResponse, method: BaseMethod[Any]) -> Never:
        # ruff: noqa: PLR2004
        code: str = response.data.get("code") or response.data.get("error_code", "")
        error: str = response.data.get("error") or response.data.get("error_data", "")
        message: str = response.data.get("message", "")

        if response.status_code == 400:
            raise MaxBotBadRequestError(code, error, message)
        if response.status_code == 401:
            raise MaxBotUnauthorizedError(code, error, message)
        if response.status_code == 403:
            raise MaxBotForbiddenError(code, error, message)
        if response.status_code == 404:
            raise MaxBotNotFoundError(code, error, message)
        if response.status_code == 405:
            raise MaxBotMethodNotAllowedError(code, error, message)
        if response.status_code == 429:
            raise MaxBotTooManyRequestsError(code, error, message)
        if response.status_code == 500:
            raise MaxBotUnknownServerError(code, error, message)
        if response.status_code == 503:
            raise MaxBotServiceUnavailableError(code, error, message)
        raise MaxBotApiError(code, error, message)

    def validate_response(self, response: HTTPResponse, method: BaseMethod) -> None:
        if (
            response.ok
            and isinstance(response.data, dict)
            and (
                response.data.get("error_code")
                or response.data.get("success", None) is False
            )
        ):
            loggers.bot_session.warning(
                "Patch the status code from %d to 400 due to an error on the MAX API",
                response.status_code,
            )
            response.status_code = 400
