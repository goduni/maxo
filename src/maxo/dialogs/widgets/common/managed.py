from typing import Any, Generic, TypeVar

from maxo.dialogs.api.internal import Widget
from maxo.dialogs.api.protocols import DialogManager

W = TypeVar("W", bound=Widget)


class ManagedWidget(Generic[W]):
    def __init__(self, widget: W, manager: DialogManager) -> None:
        self.widget = widget
        self.manager = manager

    def __getattr__(self, item: str) -> Any:
        return getattr(self.widget, item)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.widget!r}>"
