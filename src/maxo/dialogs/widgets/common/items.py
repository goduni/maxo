from collections.abc import Callable, Sequence
from operator import itemgetter
from typing import Any

from maxo.dialogs.integrations.magic_filter import DialogMagic

ItemsGetter = Callable[[dict], Sequence]
ItemsGetterVariant = str | ItemsGetter | DialogMagic | Sequence


def _get_identity(items: Sequence) -> ItemsGetter:
    def identity(data: Any) -> Sequence:
        return items

    return identity


def _get_magic_getter(f: DialogMagic) -> ItemsGetter:
    def items_magic(data: dict) -> Sequence:
        items = f.resolve(data)
        if isinstance(items, Sequence):
            return items
        return []

    return items_magic


def get_items_getter(attr_val: ItemsGetterVariant) -> ItemsGetter:
    if isinstance(attr_val, str):
        return itemgetter(attr_val)
    if isinstance(attr_val, DialogMagic):
        return _get_magic_getter(attr_val)
    if isinstance(attr_val, Callable):
        return attr_val
    return _get_identity(attr_val)
