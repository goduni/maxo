from collections.abc import Sequence
from datetime import datetime
from typing import Any

from adaptix import P, Retort, dumper, loader
from aiohttp import ClientResponse
from retejo.core import AdaptixFactory, Factory, RequestContextProxy
from retejo.http import (
    HttpMethod,
    HttpRequest,
    http_method_dumper_provider,
    http_response_loader_provider,
)
from retejo.http.clients.aiohttp import AiohttpClient
from retejo.http.entities import HttpResponse
from retejo.http.markers import (
    BodyMarker,
    FormMarker,
    HeaderMarker,
    QueryParamMarker,
    UrlVarMarker,
)
from retejo.marker_tools import for_marker

from maxo._internal._adaptix.concat_provider import concat_provider
from maxo._internal._adaptix.has_tag_provider import has_tag_provider
from maxo.bot.warming_up import WarmingUpType, warming_up_retort
from maxo.enums import (
    AttachmentRequestType,
    AttachmentType,
    KeyboardButtonType,
    MarkupElementType,
)
from maxo.enums.text_fromat import TextFormat
from maxo.errors.api import (
    MaxBotBadRequestError,
    MaxBotForbiddenError,
    MaxBotMethodNotAllowedError,
    MaxBotNotFoundError,
    MaxBotServiceUnavailableError,
    MaxBotTooManyRequestsError,
    MaxBotUnauthorizedError,
    RetvalReturnedServerException,
)
from maxo.omit import Omittable
from maxo.routing.updates.bot_added import BotAdded
from maxo.routing.updates.bot_removed import BotRemoved
from maxo.routing.updates.bot_started import BotStarted
from maxo.routing.updates.chat_title_changed import ChatTitileChanged
from maxo.routing.updates.message_callback import MessageCallback
from maxo.routing.updates.message_chat_created import MessageChatCreated
from maxo.routing.updates.message_created import MessageCreated
from maxo.routing.updates.message_edited import MessageEdited
from maxo.routing.updates.message_removed import MessageRemoved
from maxo.routing.updates.user_added import UserAdded
from maxo.routing.updates.user_removed import UserRemoved
from maxo.types import InlineKeyboardAttachment
from maxo.types.audio_attachment import AudioAttachment
from maxo.types.audio_attachment_request import AudioAttachmentRequest
from maxo.types.callback_keyboard_button import CallbackKeyboardButton
from maxo.types.contact_attachment import ContactAttachment
from maxo.types.contact_attachment_request import ContactAttachmentRequest
from maxo.types.file_attachment import FileAttachment
from maxo.types.file_attachment_request import FileAttachmentRequest
from maxo.types.image_attachment import ImageAttachment
from maxo.types.image_attachment_request import ImageAttachmentRequest
from maxo.types.inline_keyboard_attachment_request import (
    InlineKeyboardAttachmentRequest,
)
from maxo.types.link_keyboard_button import LinkKeyboardButton
from maxo.types.location_attachment import LocationAttachment
from maxo.types.location_attachment_request import LocationAttachmentRequest
from maxo.types.markup_elements import (
    EmphasizedMarkupElement,
    HeadingMarkupElement,
    HighlightedMarkupElement,
    LinkMarkupElement,
    MonospacedMarkupElements,
    StrikethroughMarkupElement,
    StrongMarkupElement,
    UnderlineMarkupElement,
    UserMentionMarkupElement,
)
from maxo.types.message_keyboard_button import MessageKeyboardButton
from maxo.types.open_app_keyboard_button import OpenAppKeyboardButton
from maxo.types.request_contact_keyboard_button import RequestContactKeyboardButton
from maxo.types.request_geo_location_button import RequestGeoLocationKeyboardButton
from maxo.types.share_attachment import ShareAttachment
from maxo.types.share_attachment_request import ShareAttachmentRequest
from maxo.types.sticker_attachment import StickerAttachment
from maxo.types.sticker_attachment_request import StickerAttachmentRequest
from maxo.types.video_attachment import VideoAttachment
from maxo.types.video_attachment_request import VideoAttachmentRequest

_has_tag_providers = concat_provider(
    # ---> UpdateType <---
    has_tag_provider(BotAdded, "update_type", "bot_added"),
    has_tag_provider(UserAdded, "update_type", "user_added"),
    has_tag_provider(MessageRemoved, "update_type", "message_removed"),
    has_tag_provider(MessageEdited, "update_type", "message_edited"),
    has_tag_provider(MessageCallback, "update_type", "message_callback"),
    has_tag_provider(MessageChatCreated, "update_type", "message_chat_created"),
    has_tag_provider(MessageCreated, "update_type", "message_created"),
    has_tag_provider(BotStarted, "update_type", "bot_started"),
    has_tag_provider(BotRemoved, "update_type", "bot_removed"),
    has_tag_provider(ChatTitileChanged, "update_type", "chat_title_changed"),
    has_tag_provider(UserRemoved, "update_type", "user_removed"),
    # ---> AttachmentType <---
    has_tag_provider(AudioAttachment, "type", AttachmentType.AUDIO),
    has_tag_provider(ContactAttachment, "type", AttachmentType.CONTACT),
    has_tag_provider(FileAttachment, "type", AttachmentType.FILE),
    has_tag_provider(ImageAttachment, "type", AttachmentType.IMAGE),
    has_tag_provider(InlineKeyboardAttachment, "type", AttachmentType.INLINE_KEYBOARD),
    has_tag_provider(LocationAttachment, "type", AttachmentType.LOCATION),
    has_tag_provider(ShareAttachment, "type", AttachmentType.SHARE),
    has_tag_provider(StickerAttachment, "type", AttachmentType.STICKER),
    has_tag_provider(VideoAttachment, "type", AttachmentType.VIDEO),
    # ---> MarkupElementType <---
    has_tag_provider(EmphasizedMarkupElement, "type", MarkupElementType.EMPHASIZED),
    has_tag_provider(HeadingMarkupElement, "type", MarkupElementType.HEADING),
    has_tag_provider(HighlightedMarkupElement, "type", MarkupElementType.HIGHLIGHTED),
    has_tag_provider(LinkMarkupElement, "type", MarkupElementType.LINK),
    has_tag_provider(MonospacedMarkupElements, "type", MarkupElementType.MONOSPACED),
    has_tag_provider(
        StrikethroughMarkupElement,
        "type",
        MarkupElementType.STRIKETHROUGH,
    ),
    has_tag_provider(StrongMarkupElement, "type", MarkupElementType.STRONG),
    has_tag_provider(UnderlineMarkupElement, "type", MarkupElementType.UNDERLINE),
    has_tag_provider(UserMentionMarkupElement, "type", MarkupElementType.USER_MENTION),
    # ---> AttachmentRequestType <---
    has_tag_provider(ImageAttachmentRequest, "type", AttachmentRequestType.IMAGE),
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
    has_tag_provider(CallbackKeyboardButton, "type", KeyboardButtonType.CALLBACK),
    has_tag_provider(LinkKeyboardButton, "type", KeyboardButtonType.LINK),
    has_tag_provider(
        RequestContactKeyboardButton,
        "type",
        KeyboardButtonType.REQUEST_CONTACT,
    ),
    has_tag_provider(
        RequestGeoLocationKeyboardButton,
        "type",
        KeyboardButtonType.REQUEST_GEO_LOCATION,
    ),
    has_tag_provider(
        OpenAppKeyboardButton,
        "type",
        KeyboardButtonType.OPEN_APP,
    ),
    has_tag_provider(
        MessageKeyboardButton,
        "type",
        KeyboardButtonType.MESSAGE,
    ),
)


class MaxApiClient(AiohttpClient):
    def __init__(
        self,
        token: str,
        warming_up: bool,
        text_format: TextFormat | None = None,
        base_url: str = "https://platform-api.max.ru/",
    ) -> None:
        self._token = token
        self._warming_up = warming_up
        self._text_format = text_format
        super().__init__(base_url=base_url)

    def init_method_dumper(self) -> Factory:
        retort = Retort(
            recipe=[
                http_method_dumper_provider(),
                _has_tag_providers,
                dumper(
                    for_marker(QueryParamMarker, P[None]),
                    lambda _: "null",
                ),
                dumper(
                    for_marker(QueryParamMarker, P[bool]),
                    lambda item: int(item),
                ),
                dumper(
                    for_marker(QueryParamMarker, P[Sequence[str]] | P[Sequence[int]]),
                    lambda item: ",".join(item),
                ),
                dumper(
                    for_marker(BodyMarker, P[Omittable[TextFormat | None]]),
                    lambda item: item or self._text_format,
                ),
            ],
        )
        if self._warming_up:
            retort = warming_up_retort(retort, warming_up=WarmingUpType.METHOD)
        return AdaptixFactory(retort)

    def init_response_loader(self) -> Factory:
        retort = Retort(
            recipe=[
                http_response_loader_provider(),
                _has_tag_providers,
                loader(P[datetime], lambda x: datetime.fromtimestamp(x / 1000)),
            ],
        )
        if self._warming_up:
            retort = warming_up_retort(retort, warming_up=WarmingUpType.TYPES)
        return AdaptixFactory(retort)

    def method_to_request(self, method: HttpMethod[Any]) -> HttpRequest:
        request_context = RequestContextProxy(self._method_dumper.dump(method))

        url_vars = request_context.get(UrlVarMarker)
        if url_vars is None:
            url = method.__url__
        else:
            url = method.__url__.format_map(url_vars)

        # TODO: Вынести в retort dumper?
        headers: dict[str, Any] = request_context.get(HeaderMarker) or {}
        headers["Authorization"] = headers.get("Authorization", self._token)

        return HttpRequest(
            url=url,
            http_method=method.__http_method__,
            body=request_context.get(BodyMarker),
            headers=headers,
            query_params=request_context.get(QueryParamMarker),
            form=request_context.get(FormMarker),
            context=request_context,
        )

    async def retrieve_response_data(
        self,
        raw_response: ClientResponse,
    ) -> Any:
        text = await raw_response.text()
        if "retval" in text:
            raise RetvalReturnedServerException

        return await super().retrieve_response_data(raw_response)

    async def handle_error_response(
        self,
        response: HttpResponse[ClientResponse],
    ) -> None:
        # TODO: WTF???
        code, message = (
            response.data.get("code", -1),
            response.data.get("message", ""),
        )

        if response.status_code == 400:
            raise MaxBotBadRequestError(code, message)
        if response.status_code == 401:
            raise MaxBotUnauthorizedError(code, message)
        if response.status_code == 403:
            raise MaxBotForbiddenError(code, message)
        if response.status_code == 404:
            raise MaxBotNotFoundError(code, message)
        if response.status_code == 405:
            raise MaxBotMethodNotAllowedError(code, message)
        if response.status_code == 429:
            raise MaxBotTooManyRequestsError(code, message)
        if response.status_code == 503:
            raise MaxBotServiceUnavailableError(code, message)

        return await super().handle_error_response(response)
