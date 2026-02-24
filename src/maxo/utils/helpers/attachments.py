# ruff: noqa: E501

from typing import assert_never

from maxo.types import (
    Attachments,
    AttachmentsRequests,
    AudioAttachmentRequest,
    ContactAttachmentRequest,
    FileAttachmentRequest,
    InlineKeyboardAttachment,
    InlineKeyboardAttachmentRequest,
    Keyboard,
    LocationAttachment,
    LocationAttachmentRequest,
    PhotoAttachmentRequest,
    ShareAttachment,
    ShareAttachmentRequest,
    StickerAttachmentRequest,
    VideoAttachmentRequest,
)


def request_to_attachment(request: AttachmentsRequests) -> Attachments:
    if isinstance(request, InlineKeyboardAttachmentRequest):
        return InlineKeyboardAttachment(
            payload=Keyboard(buttons=request.payload.buttons),
        )
    if isinstance(request, LocationAttachmentRequest):
        return LocationAttachment(
            latitude=float(request.latitude),
            longitude=float(request.longitude),
        )
    if isinstance(request, ShareAttachmentRequest):
        return ShareAttachment(payload=request.payload)

    if isinstance(
        request,
        (
            PhotoAttachmentRequest,
            VideoAttachmentRequest,
            AudioAttachmentRequest,
            FileAttachmentRequest,
            StickerAttachmentRequest,
            ContactAttachmentRequest,
        ),
    ):
        raise TypeError(
            f"Cannot convert {type(request).__name__} to an Attachment object directly. "
            "Request objects lack server-generated data like IDs, URLs, or resolved user info. "
            "This conversion is only possible for request types that have a 1:1 mapping of fields "
            "(e.g., LocationAttachmentRequest, InlineKeyboardAttachmentRequest).",
        )

    assert_never(request)
