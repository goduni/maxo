from maxo.types.base import MaxoType


class StickerAttachmentRequestPayload(MaxoType):
    """
    Args:
        code: Код стикера
    """

    code: str
