import dataclasses
from collections.abc import Callable
from typing import Any

from maxo.dialogs.api.internal import RawKeyboard, Widget
from maxo.dialogs.api.protocols import DialogManager, DialogProtocol
from maxo.dialogs.manager.sub_manager import SubManager
from maxo.dialogs.widgets.common import ManagedWidget, WhenCondition
from maxo.dialogs.widgets.common.items import ItemsGetterVariant, get_items_getter
from maxo.routing.updates import MessageCallback

from .base import Keyboard

ItemIdGetter = Callable[[Any], str | int]


class ListGroup(Keyboard):
    def __init__(
        self,
        *buttons: Keyboard,
        id: str,
        item_id_getter: ItemIdGetter,
        items: ItemsGetterVariant,
        when: WhenCondition = None,
    ) -> None:
        super().__init__(id=id, when=when)
        self.buttons = buttons
        self.item_id_getter = item_id_getter
        self.items_getter = get_items_getter(items)

    async def _render_keyboard(
        self,
        data: dict,
        manager: DialogManager,
    ) -> RawKeyboard:
        kbd: RawKeyboard = []
        for pos, item in enumerate(self.items_getter(data)):
            kbd.extend(await self._render_item(pos, item, data, manager))
        return kbd

    async def _render_item(
        self,
        pos: int,
        item: Any,
        data: dict,
        manager: DialogManager,
    ) -> RawKeyboard:
        kbd: RawKeyboard = []
        data = {"data": data, "item": item, "pos": pos + 1, "pos0": pos}
        item_id = str(self.item_id_getter(item))
        sub_manager = SubManager(
            widget=self,
            manager=manager,
            widget_id=self.widget_id,
            item_id=item_id,
        )
        for b in self.buttons:
            b_kbd = await b.render_keyboard(data, sub_manager)
            for row in b_kbd:
                for btn in row:
                    if btn.payload:
                        btn.payload = self._item_payload(
                            f"{item_id}:{btn.payload}",
                        )
            kbd.extend(b_kbd)
        return kbd

    def find(self, widget_id: str) -> Widget | None:
        if widget_id == self.widget_id:
            return self
        for btn in self.buttons:
            widget = btn.find(widget_id)
            if widget:
                return widget
        return None

    async def _process_item_callback(
        self,
        callback: MessageCallback,
        data: str,
        dialog: DialogProtocol,
        manager: DialogManager,
    ) -> bool:
        item_id, payload = data.split(":", maxsplit=1)

        cleaned_callback = dataclasses.replace(callback.callback, payload=payload)
        cleaned_event = dataclasses.replace(callback, callback=cleaned_callback)

        sub_manager = SubManager(
            widget=self,
            manager=manager,
            widget_id=self.widget_id,
            item_id=item_id,
        )
        for b in self.buttons:
            if await b.process_callback(cleaned_event, dialog, sub_manager):
                return True
        return False

    def managed(self, manager: DialogManager) -> "ManagedListGroup":
        return ManagedListGroup(self, manager)


class ManagedListGroup(ManagedWidget[ListGroup]):
    def find_for_item(self, widget_id: str, item_id: str) -> Widget | None:
        """Find widget for specific item_id."""
        widget = self.widget.find(widget_id)
        if widget:
            return widget.managed(
                SubManager(
                    widget=self.widget,
                    manager=self.manager,
                    widget_id=self.widget.widget_id,
                    item_id=item_id,
                ),
            )
        return None
