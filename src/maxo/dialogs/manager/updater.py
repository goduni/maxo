import asyncio
from contextvars import copy_context

from maxo import Bot, Dispatcher
from maxo.dialogs.api.entities import DialogUpdate, DialogUpdateEvent


class Updater:
    def __init__(self, dp: Dispatcher):
        if not isinstance(dp, Dispatcher):
            raise TypeError("Root router must be Dispatcher.")
        self.dp = dp

    async def notify(self, update: DialogUpdate, bot: Bot) -> None:
        def callback():
            asyncio.create_task(  # noqa: RUF006
                self._process_update(update, bot),
            )

        asyncio.get_running_loop().call_soon(callback, context=copy_context())

    async def _process_update(self, update: DialogUpdate, bot: Bot) -> None:
        event = update.event
        await self.dp.feed_update(
            DialogUpdate(
                aiogd_update=DialogUpdateEvent(
                    bot=bot,
                    sender=event.sender,
                    chat=event.chat,
                    **self.dp.workflow_data,
                ),
            ),
            bot,
        )
