from dataclasses import dataclass
from typing import Any, TypeVar, dataclass_transform

T = TypeVar("T")


@dataclass_transform(frozen_default=False, kw_only_default=False)
class _MaxoErrorMetaClass(type):
    def __new__(
        cls,
        name: str,
        bases: tuple[Any, ...],
        namespace: dict[str, Any],
    ) -> Any:
        class_ = super().__new__(cls, name, bases, namespace)
        return dataclass(
            slots=False,
            frozen=False,
            kw_only=False,
        )(class_)


class MaxoError(Exception, metaclass=_MaxoErrorMetaClass):
    pass
