from pathlib import Path

from maxo.dialogs.api.entities import MediaAttachment
from maxo.dialogs.api.protocols import DialogManager
from maxo.dialogs.widgets.common import WhenCondition
from maxo.dialogs.widgets.text import Const, Text
from maxo.enums import AttachmentType

from .base import Media


class StaticMedia(Media):
    def __init__(
        self,
        *,
        path: Text | str | Path | None = None,
        url: Text | str | None = None,
        type: AttachmentType = AttachmentType.IMAGE,
        use_pipe: bool = False,
        media_params: dict | None = None,
        when: WhenCondition = None,
    ):
        super().__init__(when=when)
        if not (url or path):
            raise ValueError("Neither url nor path are provided")
        self.type = type
        if isinstance(path, Path):
            path = Const(str(path))
        elif isinstance(path, str):
            path = Const(path)
        self.path = path
        if isinstance(url, str):
            url = Const(url)
        self.url = url
        self.use_pipe = use_pipe
        self.media_params = media_params or {}

    async def _render_media(
        self,
        data: dict,
        manager: DialogManager,
    ) -> MediaAttachment | None:
        if self.url:
            url = await self.url.render_text(data, manager)
        else:
            url = None
        if self.path:
            path = await self.path.render_text(data, manager)
        else:
            path = None

        return MediaAttachment(
            type=self.type,
            url=url,
            path=path,
            use_pipe=self.use_pipe,
            **self.media_params,
        )
