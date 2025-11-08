import logging
import os
from typing import Any

from maxo import Bot, Ctx, Dispatcher
from maxo.routing.filters.base import BaseFilter
from maxo.routing.interfaces.middleware import BaseMiddleware, NextMiddleware
from maxo.routing.updates.message_created import MessageCreated
from maxo.tools.facades import MessageCreatedFacade
from maxo.tools.long_polling.long_polling import LongPolling


class OuterMiddleware(BaseMiddleware[MessageCreated]):
    async def __call__(
        self,
        update: MessageCreated,
        ctx: Ctx[MessageCreated],
        next: NextMiddleware[MessageCreated],
    ) -> Any:
        print("Исполнится перед фильтрами")  # noqa: T201
        result = await next(ctx)
        print("Исполнится после фильтров")  # noqa: T201
        return result


class InnerMiddleware(BaseMiddleware[MessageCreated]):
    async def __call__(
        self,
        update: MessageCreated,
        ctx: Ctx[MessageCreated],
        next: NextMiddleware[MessageCreated],
    ) -> Any:
        print("Исполнится перед хендлером")  # noqa: T201
        result = await next(ctx)
        print("Исполнится после хендлера")  # noqa: T201
        return result


class ContainsTextFilter(BaseFilter[MessageCreated]):
    def __init__(self, text: str) -> None:
        self._text = text

    async def __call__(
        self,
        update: MessageCreated,
        ctx: Ctx[MessageCreated],
    ) -> bool:
        if update.message.body is None:
            return False
        if update.message.body.text is None:
            return False

        return self._text in update.message.body.text


dispatcher = Dispatcher()
dispatcher.message_created.middleware.inner(InnerMiddleware())
dispatcher.message_created.middleware.outer(OuterMiddleware())


@dispatcher.message_created(
    (ContainsTextFilter("gojo") & ContainsTextFilter("maki"))
    | ContainsTextFilter("sukuna")
)
async def echo_handler(
    update: MessageCreated,
    ctx: Ctx[MessageCreated],
    facade: MessageCreatedFacade,
) -> None:
    print("Исполнение хендлера")  # noqa: T201


logging.basicConfig(level=logging.INFO)
bot = Bot(os.environ["TOKEN"])
LongPolling(dispatcher).run(bot)
