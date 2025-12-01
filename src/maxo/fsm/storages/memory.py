from asyncio import Lock
from collections import defaultdict
from collections.abc import AsyncIterator, Hashable, MutableMapping
from contextlib import asynccontextmanager
from copy import copy
from typing import Any

from maxo.fsm.key_builder import (
    BaseKeyBuilder,
    DefaultKeyBuilder,
    StorageKey,
    StorageKeyType,
)
from maxo.fsm.state import State
from maxo.fsm.storages.base import BaseEventIsolation, BaseStorage


class MemoryStorage(BaseStorage):
    _state: MutableMapping[str, str | None]
    _data: MutableMapping[str, MutableMapping[str, Any]]

    __slots__ = ("_data", "_key_builder", "_state")

    def __init__(
        self,
        key_builder: BaseKeyBuilder | None = None,
    ) -> None:
        self._data = {}
        self._state = {}

        if key_builder is None:
            key_builder = DefaultKeyBuilder()
        self._key_builder = key_builder

    async def set_state(self, key: StorageKey, state: State | None = None) -> None:
        built_key = self._key_builder.build(key, StorageKeyType.STATE)

        if state is None:
            self._state[built_key] = None
        else:
            self._state[built_key] = state.state

    async def get_state(self, key: StorageKey) -> str | None:
        built_key = self._key_builder.build(key, StorageKeyType.STATE)
        return self._state.get(built_key)

    async def set_data(self, key: StorageKey, data: MutableMapping[str, Any]) -> None:
        built_key = self._key_builder.build(key, StorageKeyType.DATA)
        self._data[built_key] = copy(data)

    async def get_data(self, key: StorageKey) -> MutableMapping[str, Any]:
        built_key = self._key_builder.build(key, StorageKeyType.DATA)
        return copy(self._data.get(built_key, {}))

    async def close(self) -> None:
        self._data.clear()
        self._state.clear()


class SimpleEventIsolation(BaseEventIsolation):
    __slots__ = ("_key_builder", "_locks")

    def __init__(
        self,
        key_builder: BaseKeyBuilder | None = None,
    ) -> None:
        if key_builder is None:
            key_builder = DefaultKeyBuilder()
        self._key_builder = key_builder

        self._locks: defaultdict[Hashable, Lock] = defaultdict(Lock)

    @asynccontextmanager
    async def lock(self, key: StorageKey) -> AsyncIterator[None]:
        built_key = self._key_builder.build(key, StorageKeyType.LOCK)

        lock = self._locks[built_key]
        async with lock:
            yield

    async def close(self) -> None:
        self._locks.clear()


class DisabledEventIsolation(BaseEventIsolation):
    @asynccontextmanager
    async def lock(self, key: StorageKey) -> AsyncIterator[None]:  # noqa: ARG002
        yield

    async def close(self) -> None:
        pass
