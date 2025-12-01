from maxo.dialogs.api.entities import MediaAttachment
from maxo.dialogs.api.internal import MediaWidget
from maxo.dialogs.api.protocols import DialogManager
from maxo.dialogs.widgets.common import BaseWidget, WhenCondition, Whenable


class Media(Whenable, BaseWidget, MediaWidget):
    def __init__(self, when: WhenCondition = None):
        super().__init__(when=when)

    async def render_media(
        self,
        data: dict,
        manager: DialogManager,
    ) -> MediaAttachment | None:
        if not self.is_(data, manager):
            return None
        return await self._render_media(data, manager)

    async def _render_media(
        self,
        data: dict,
        manager: DialogManager,
    ) -> MediaAttachment | None:
        return None

    def __or__(self, other: "Media") -> "Or":
        # reduce nesting
        if isinstance(other, Or):
            return NotImplemented
        return Or(self, other)

    def __ror__(self, other: "Media") -> "Or":
        # reduce nesting
        return Or(other, self)


class Or(Media):
    def __init__(self, *widgets: Media):
        super().__init__()
        self.widgets = widgets

    async def _render_media(
        self,
        data: dict,
        manager: DialogManager,
    ) -> MediaAttachment | None:
        for widget in self.widgets:
            res = await widget.render_media(data, manager)
            if res:
                return res
        return None

    def __ior__(self, other: Media) -> "Or":
        self.widgets += (other,)
        return self

    def __or__(self, other: Media) -> "Or":
        # reduce nesting
        return Or(*self.widgets, other)

    def __ror__(self, other: Media) -> "Or":
        # reduce nesting
        return Or(other, *self.widgets)
