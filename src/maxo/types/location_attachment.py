from maxo.enums.attachment_type import AttachmentType
from maxo.types.attachment import Attachment


class LocationAttachment(Attachment):
    """
    Args:
        latitude: Широта
        longitude: Долгота
        type:
    """

    type: AttachmentType = AttachmentType.LOCATION

    latitude: float
    longitude: float
