from maxo.types.audio_attachment import AudioAttachment
from maxo.types.audio_attachment_request import AudioAttachmentRequest
from maxo.types.contact_attachment import ContactAttachment
from maxo.types.contact_attachment_request import ContactAttachmentRequest
from maxo.types.file_attachment import FileAttachment
from maxo.types.file_attachment_request import FileAttachmentRequest
from maxo.types.inline_keyboard_attachment import InlineKeyboardAttachment
from maxo.types.inline_keyboard_attachment_request import (
    InlineKeyboardAttachmentRequest,
)
from maxo.types.location_attachment import LocationAttachment
from maxo.types.location_attachment_request import LocationAttachmentRequest
from maxo.types.photo_attachment import PhotoAttachment
from maxo.types.photo_attachment_request import PhotoAttachmentRequest
from maxo.types.share_attachment import ShareAttachment
from maxo.types.share_attachment_request import ShareAttachmentRequest
from maxo.types.sticker_attachment import StickerAttachment
from maxo.types.sticker_attachment_request import StickerAttachmentRequest
from maxo.types.video_attachment import VideoAttachment
from maxo.types.video_attachment_request import VideoAttachmentRequest

MediaAttachments = PhotoAttachment | VideoAttachment | AudioAttachment | FileAttachment
Attachments = (
    MediaAttachments
    | StickerAttachment
    | ContactAttachment
    | InlineKeyboardAttachment
    | ShareAttachment
    | LocationAttachment
)
MediaAttachmentsRequests = (
    PhotoAttachmentRequest
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
