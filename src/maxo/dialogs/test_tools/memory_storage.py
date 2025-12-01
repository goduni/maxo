import json
from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Optional

from maxo.fsm import State
from maxo.fsm.key_builder import StorageKey
from maxo.fsm.storages.base import BaseStorage

StateType = Optional[str | State]


@dataclass
class MemoryStorageRecord:
    data: str = "{}"
    state: str | None = None


class JsonMemoryStorage(BaseStorage):
    storage: dict[StorageKey, MemoryStorageRecord]

    def __init__(self) -> None:
        self.storage = defaultdict(MemoryStorageRecord)

    async def close(self) -> None:
        pass

    async def set_state(
        self,
        key: StorageKey,
        state: StateType = None,
    ) -> None:
        state_value = state.state if isinstance(state, State) else state
        self.storage[key].state = state_value

    async def get_state(self, key: StorageKey) -> str | None:
        return self.storage[key].state

    async def set_data(self, key: StorageKey, data: dict[str, Any]) -> None:
        self.storage[key].data = json.dumps(data)

    async def get_data(self, key: StorageKey) -> dict[str, Any]:
        return json.loads(self.storage[key].data)
