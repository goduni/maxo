
from maxo.types.audio_attachment_request import AudioAttachmentRequest
from maxo.types.contact_attachment_request import ContactAttachmentRequest
from maxo.types.file_attachment_request import FileAttachmentRequest
from maxo.types.image_attachment_request import ImageAttachmentRequest
from maxo.types.inline_keyboard_attachment_request import (
    InlineKeyboardAttachmentRequest,
)
from maxo.types.location_attachment_request import LocationAttachmentRequest
from maxo.types.share_attachment_request import ShareAttachmentRequest
from maxo.types.sticker_attachment_request import StickerAttachmentRequest
from maxo.types.video_attachment_request import VideoAttachmentRequest

MediaAttachmentsRequests = (
    ImageAttachmentRequest
    | VideoAttachmentRequest
    | AudioAttachmentRequest
    | FileAttachmentRequest
)

AttachmentsRequests = (
    MediaAttachmentsRequests
    | StickerAttachmentRequest
    | ContactAttachmentRequest
    | InlineKeyboardAttachmentRequest
    | LocationAttachmentRequest
    | ShareAttachmentRequest
)
