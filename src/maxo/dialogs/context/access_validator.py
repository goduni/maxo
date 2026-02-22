from logging import getLogger

from maxo.dialogs import ChatEvent
from maxo.dialogs.api.entities import Context, Stack
from maxo.dialogs.api.protocols import StackAccessValidator
from maxo.routing.ctx import Ctx
from maxo.routing.middlewares.update_context import EVENT_FROM_USER_KEY
from maxo.types import User

logger = getLogger(__name__)


class DefaultAccessValidator(StackAccessValidator):
    async def is_allowed(
        self,
        stack: Stack,
        context: Context | None,
        event: ChatEvent,
        ctx: Ctx,
    ) -> bool:
        access_settings = context.access_settings if context else stack.access_settings

        # if everything is disabled, it is allowed
        if access_settings is None:
            return True
        if not (access_settings.user_ids or access_settings.custom):
            return True

        user: User = ctx[EVENT_FROM_USER_KEY]
        if user.id in access_settings.user_ids:  # noqa: SIM103
            return True

        return False
