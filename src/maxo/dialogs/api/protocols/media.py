from abc import abstractmethod
from typing import Protocol

from maxo.dialogs.api.entities import MediaId
from maxo.enums import AttachmentType


class MediaIdStorageProtocol(Protocol):
    @abstractmethod
    async def get_media_id(
        self,
        path: str | None,
        url: str | None,
        type: AttachmentType,
    ) -> MediaId | None:
        raise NotImplementedError

    @abstractmethod
    async def save_media_id(
        self,
        path: str | None,
        url: str | None,
        type: AttachmentType,
        media_id: MediaId,
    ) -> None:
        raise NotImplementedError
