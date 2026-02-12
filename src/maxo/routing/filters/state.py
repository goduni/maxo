from inspect import isclass
from typing import Any

from maxo import Ctx
from maxo.fsm.state import State, StatesGroup, any_state
from maxo.routing.filters import BaseFilter


class StateFilter(BaseFilter[Any]):
    __slots__ = ("_states",)

    def __init__(
        self,
        *states: State | StatesGroup | type[StatesGroup] | None | str,
    ) -> None:
        self._states = states

    async def __call__(self, update: Any, ctx: Ctx) -> bool:  # noqa: ARG002
        raw_state = ctx.get("raw_state")

        for state in self._states:
            if (isinstance(state, str) or state is None) and (
                state in (any_state, raw_state)
            ):
                return True
            if isinstance(state, State) and raw_state == state:
                return True
            if (
                isclass(state)
                and issubclass(state, StatesGroup)
                and raw_state in StatesGroup
            ):
                return True

        return False
