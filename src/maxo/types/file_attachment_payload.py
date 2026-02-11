from maxo.types.attachment_payload import AttachmentPayload


class FileAttachmentPayload(AttachmentPayload):
    """
    Args:
        token: Используйте `token`, если вы пытаетесь повторно использовать одно и то же вложение в другом сообщении.
    """

    token: str
