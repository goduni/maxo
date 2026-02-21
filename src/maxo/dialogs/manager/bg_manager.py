import logging
from datetime import UTC, datetime
from typing import Any

from maxo import Bot, Dispatcher
from maxo.dialogs.api.entities import (
    DEFAULT_STACK_ID,
    AccessSettings,
    Data,
    DialogAction,
    DialogStartEvent,
    DialogSwitchEvent,
    DialogUpdateEvent,
    EventContext,
    ShowMode,
    StartMode,
)
from maxo.dialogs.api.internal import FakeUser
from maxo.dialogs.api.protocols import BaseDialogManager, BgManagerFactory
from maxo.dialogs.manager.updater import Updater
from maxo.dialogs.utils import is_user_loaded
from maxo.enums import ChatType
from maxo.fsm import State
from maxo.routing.interfaces import BaseRouter
from maxo.types import Recipient, User

logger = logging.getLogger(__name__)


class BgManager(BaseDialogManager):
    def __init__(
        self,
        user: User,
        chat_id: int | None,
        bot: Bot,
        dp: Dispatcher,
        intent_id: str | None,
        stack_id: str | None,
        load: bool = False,
    ) -> None:
        self._event_context = EventContext(
            chat_id=chat_id,
            user_id=user.id,
            chat_type=ChatType.CHAT,  # TODO: Узнать тип чата
            user=user,
            chat=None,
            bot=bot,
        )
        self._router = dp
        self._updater = Updater(dp)
        self.intent_id = intent_id
        self.stack_id = stack_id
        self.load = load

    def _get_fake_user(self, user_id: int | None = None) -> User:
        if user_id is None or user_id == self._event_context.user.id:
            return self._event_context.user
        return FakeUser(
            user_id=user_id,
            is_bot=False,
            first_name="",
            last_activity_time=datetime.now(UTC),
        )

    def bg(
        self,
        user_id: int | None = None,
        chat_id: int | None = None,
        stack_id: str | None = None,
        load: bool = False,
    ) -> "BaseDialogManager":
        user = self._get_fake_user(user_id)

        new_event_context = EventContext(
            bot=self._event_context.bot,
            user=user,
            chat_id=chat_id,
            user_id=user_id,
            chat_type=ChatType.CHAT,  # TODO: Узнать тип чата
            chat=None,
        )
        if stack_id is None:
            if self._event_context == new_event_context:
                stack_id = self.stack_id
                intent_id = self.intent_id
            else:
                stack_id = DEFAULT_STACK_ID
                intent_id = None
        else:
            intent_id = None

        return BgManager(
            user=new_event_context.user,
            chat_id=new_event_context.chat_id,
            bot=new_event_context.bot,
            dp=self._router,
            intent_id=intent_id,
            stack_id=stack_id,
            load=load,
        )

    def _base_event_params(self) -> dict[str, Any]:
        return {
            "user": self._event_context.user,
            "recipient": Recipient(
                user_id=self._event_context.user.id,
                chat_id=self._event_context.chat_id,
                chat_type=self._event_context.chat_type,
            ),
            "bot": self._event_context.bot,
            "intent_id": self.intent_id,
            "stack_id": self.stack_id,
        }

    async def _notify(self, event: DialogUpdateEvent) -> None:
        bot = self._event_context.bot
        await self._updater.notify(update=event, bot=bot)

    async def _load(self) -> None:
        if self.load:
            bot = self._event_context.bot
            if not is_user_loaded(self._event_context.user):
                logger.debug(
                    "load user %s from chat %s",
                    self._event_context.user_id,
                    self._event_context.chat_id,
                )
                chat_members = await bot.get_members(
                    chat_id=self._event_context.chat_id,
                    user_ids=[self._event_context.user_id],
                )
                if chat_members:
                    self._event_context.user = chat_members[0]

    async def done(
        self,
        result: Any = None,
        show_mode: ShowMode | None = None,
    ) -> None:
        await self._load()
        await self._notify(
            DialogUpdateEvent(
                action=DialogAction.DONE,
                data=result,
                show_mode=show_mode,
                **self._base_event_params(),
            ),
        )

    async def start(
        self,
        state: State,
        data: Data = None,
        mode: StartMode = StartMode.NORMAL,
        show_mode: ShowMode | None = None,
        access_settings: AccessSettings | None = None,
    ) -> None:
        await self._load()
        await self._notify(
            DialogStartEvent(
                action=DialogAction.START,
                data=data,
                new_state=state,
                mode=mode,
                show_mode=show_mode,
                access_settings=access_settings,
                **self._base_event_params(),
            ),
        )

    async def switch_to(
        self,
        state: State,
        show_mode: ShowMode | None = None,
    ) -> None:
        await self._load()
        await self._notify(
            DialogSwitchEvent(
                action=DialogAction.SWITCH,
                data={},
                new_state=state,
                show_mode=show_mode,
                **self._base_event_params(),
            ),
        )

    async def update(
        self,
        data: dict,
        show_mode: ShowMode | None = None,
    ) -> None:
        await self._load()
        await self._notify(
            DialogUpdateEvent(
                action=DialogAction.UPDATE,
                data=data,
                show_mode=show_mode,
                **self._base_event_params(),
            ),
        )


class BgManagerFactoryImpl(BgManagerFactory):
    def __init__(self, router: BaseRouter) -> None:
        self._router = router

    def bg(
        self,
        bot: Bot,
        user_id: int,
        chat_id: int,
        stack_id: str | None = None,
        load: bool = False,
    ) -> "BaseDialogManager":
        user = FakeUser(
            user_id=user_id,
            is_bot=False,
            first_name="",
            last_activity_time=datetime.now(UTC),
        )
        if stack_id is None:
            stack_id = DEFAULT_STACK_ID

        return BgManager(
            user=user,
            chat_id=chat_id,
            bot=bot,
            dp=self._router,
            intent_id=None,
            stack_id=stack_id,
            load=load,
        )
