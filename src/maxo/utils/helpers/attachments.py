from decimal import Decimal
from typing import assert_never

from maxo.omit import is_not_omitted
from maxo.types import (
    AudioAttachment,
    AudioAttachmentRequest,
    ContactAttachment,
    ContactAttachmentRequest,
    FileAttachment,
    FileAttachmentRequest,
    ImageAttachment,
    ImageAttachmentRequest,
    InlineKeyboardAttachment,
    InlineKeyboardAttachmentRequest,
    Keyboard,
    LocationAttachment,
    LocationAttachmentRequest,
    ShareAttachment,
    ShareAttachmentRequest,
    StickerAttachment,
    StickerAttachmentRequest,
    VideoAttachment,
    VideoAttachmentRequest,
)
from maxo.types.attachments import Attachments
from maxo.types.request_attachments import AttachmentsRequests


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
        return ShareAttachment(
            payload=request.payload,
        )

    if isinstance(
        request,
        (
            ImageAttachmentRequest,
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


def attachment_to_request(attachment: Attachments) -> AttachmentsRequests:
    if isinstance(attachment, ImageAttachment):
        return ImageAttachmentRequest.factory(token=attachment.payload.token)
    if isinstance(attachment, VideoAttachment):
        return VideoAttachmentRequest.factory(token=attachment.payload.token)
    if isinstance(attachment, AudioAttachment):
        return AudioAttachmentRequest.factory(token=attachment.payload.token)
    if isinstance(attachment, FileAttachment):
        return FileAttachmentRequest.factory(token=attachment.payload.token)
    if isinstance(attachment, StickerAttachment):
        return StickerAttachmentRequest.factory(code=attachment.payload.code)
    if isinstance(attachment, InlineKeyboardAttachment):
        return InlineKeyboardAttachmentRequest.factory(
            buttons=attachment.payload.buttons,
        )
    if isinstance(attachment, LocationAttachment):
        return LocationAttachmentRequest(
            latitude=Decimal(str(attachment.latitude)),
            longitude=Decimal(str(attachment.longitude)),
        )
    if isinstance(attachment, ShareAttachment):
        return ShareAttachmentRequest.factory(
            url=attachment.payload.url,
            token=attachment.payload.token,
        )
    if isinstance(attachment, ContactAttachment):
        contact_id = (
            attachment.payload.max_info.id
            if is_not_omitted(attachment.payload.max_info)
            else None
        )
        return ContactAttachmentRequest.factory(
            contact_id=contact_id,
            vcf_info=attachment.payload.vcf_info,
        )

    assert_never(attachment)
