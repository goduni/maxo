from maxo.types.base import MaxoType


class PhotoAttachmentPayload(MaxoType):
    """
    Args:
        photo_id: Уникальный ID этого изображения
        token:
        url: URL изображения
    """

    photo_id: int
    token: str
    url: str
