from maxo.types.attachment_payload import AttachmentPayload


class StickerAttachmentPayload(AttachmentPayload):
    """
    Args:
        code: ID стикера
    """

    code: str
