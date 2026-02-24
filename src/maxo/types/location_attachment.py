from maxo.enums.attachment_type import AttachmentType
from maxo.types.attachment import Attachment
from maxo.types.location_attachment_request import LocationAttachmentRequest


class LocationAttachment(Attachment):
    """
    Args:
        latitude: Широта
        longitude: Долгота
        type:
    """

    type: AttachmentType = AttachmentType.LOCATION

    latitude: float
    """Широта"""
    longitude: float
    """Долгота"""

    def to_request(self) -> LocationAttachmentRequest:
        return LocationAttachmentRequest(
            latitude=self.latitude,
            longitude=self.longitude,
        )
