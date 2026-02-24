from typing import Any, ClassVar, final

from maxo.routing.ctx import Ctx
from maxo.routing.filters.base import BaseFilter


class _AlwaysBooleanFilter(BaseFilter[Any]):
    _boolean: ClassVar[bool]

    async def __call__(self, update: Any, ctx: Ctx) -> bool:
        return self._boolean


@final
class AlwaysTrueFilter(_AlwaysBooleanFilter):
    _boolean = True


@final
class AlwaysFalseFilter(_AlwaysBooleanFilter):
    _boolean = False
