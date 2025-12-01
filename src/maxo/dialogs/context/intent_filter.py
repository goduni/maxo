from maxo.dialogs.api.entities import Context
from maxo.dialogs.api.internal import CONTEXT_KEY
from maxo.fsm import StatesGroup
from maxo.routing.ctx import Ctx
from maxo.routing.filters import BaseFilter
from maxo.types import MaxoType


class IntentFilter(BaseFilter):
    def __init__(self, aiogd_intent_state_group: type[StatesGroup] | None) -> None:
        self.aiogd_intent_state_group = aiogd_intent_state_group

    async def __call__(self, update: MaxoType, ctx: Ctx) -> bool:
        if self.aiogd_intent_state_group is None:
            return True

        context: Context = ctx.get(CONTEXT_KEY)
        if not context:
            return False
        return context.state.group == self.aiogd_intent_state_group
