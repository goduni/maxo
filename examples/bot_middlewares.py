import asyncio
import logging
import os
from collections.abc import Sequence

from unihttp.http.request import HTTPRequest
from unihttp.http.response import HTTPResponse
from unihttp.middlewares.base import AsyncHandler, AsyncMiddleware

from maxo import Bot
from maxo.backoff import Backoff, BackoffConfig
from maxo.errors import MaxBotNotFoundError

logger = logging.getLogger(__name__)

_DEFAULT_BACKOFF_CONFIG = BackoffConfig(
    min_delay=1.0,
    max_delay=5.0,
    factor=1.3,
    jitter=0.1,
)


class LoggingMiddleware(AsyncMiddleware):
    async def handle(
        self,
        request: HTTPRequest,
        next_handler: AsyncHandler,
    ) -> HTTPResponse:
        logger.info("Request: %s", request)
        response = await next_handler(request)
        logger.info("Response: %s", response)
        return response


class RetryMiddleware(AsyncMiddleware):
    def __init__(
        self,
        retries: int = 3,
        backoff_config: BackoffConfig = _DEFAULT_BACKOFF_CONFIG,
        status_codes: Sequence[int] | None = None,
        exceptions: Sequence[type[Exception]] | None = None,
    ) -> None:
        self._retries = retries
        self._backoff_config = backoff_config
        self._status_codes = status_codes or (500, 502, 503, 504)
        self._exceptions = exceptions or ()

    async def handle(
        self,
        request: HTTPRequest,
        next_handler: AsyncHandler,
    ) -> HTTPResponse:
        attempt = 0
        backoff = Backoff(self._backoff_config)
        while True:
            try:
                response = await next_handler(request)
                if (
                    response.status_code in self._status_codes
                    and attempt < self._retries
                ):
                    logger.warning(
                        "Bad status code %d: %s",
                        response.status_code,
                        response,
                    )
                    backoff.next()
                    await backoff.sleep()
                    attempt += 1
                    continue
            except Exception as e:
                if (
                    self._exceptions
                    and isinstance(e, tuple(self._exceptions))
                    and attempt < self._retries
                ):
                    logger.warning("Bad exception %s", e, exc_info=e)
                    backoff.next()
                    await backoff.sleep()
                    attempt += 1
                    continue
                raise

            return response


async def main() -> None:
    bot = Bot(
        token=os.environ["TOKEN"],
        middleware=[
            LoggingMiddleware(),
            RetryMiddleware(exceptions=[MaxBotNotFoundError]),
        ],
    )
    async with bot.context():
        await bot.send_message(chat_id=-1)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    asyncio.run(main())
