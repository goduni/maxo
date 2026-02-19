from abc import abstractmethod
from typing import Any, Protocol

from typing_extensions import runtime_checkable


@runtime_checkable
class DialogMagic(Protocol):
    @abstractmethod
    def resolve(self, value: Any) -> Any:
        pass
