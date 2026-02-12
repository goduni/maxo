from typing import Any, TypeVar

from typing_extensions import TypeIs
from unihttp.omitted import Omittable as UniOmittable, Omitted as UniOmitted

Omitted = UniOmitted
Omittable = UniOmittable

_OmittedValueT = TypeVar("_OmittedValueT")


def is_omitted(value: Any) -> TypeIs[Omitted]:
    return isinstance(value, Omitted)


def is_not_omitted(value: Omittable[_OmittedValueT]) -> TypeIs[_OmittedValueT]:
    return not is_omitted(value)


def is_defined(value: Omittable[_OmittedValueT | None]) -> TypeIs[_OmittedValueT]:
    return not isinstance(value, Omitted) and value is not None


def is_not_defined(value: Omittable[_OmittedValueT | None]) -> TypeIs[Omittable[None]]:
    return not is_defined(value)


__all__ = (
    "Omittable",
    "Omitted",
    "is_defined",
    "is_not_defined",
    "is_not_omitted",
    "is_omitted",
)
