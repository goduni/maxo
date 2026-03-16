from __future__ import annotations

from typing import Any

from maxo import Bot, Dispatcher
from maxo.routing.signals import (
    AfterShutdown,
    AfterStartup,
    BeforeShutdown,
    BeforeStartup,
)
from maxo.webhook.adapters.base_adapter import BoundRequest, WebAdapter
from maxo.webhook.config.bot import BotConfig
from maxo.webhook.engines.base import WebhookEngine
from maxo.webhook.routing.base import TokenRouting
from maxo.webhook.security.security import Security


class TokenEngine(WebhookEngine):
    """
    Multi-bot webhook engine with dynamic bot resolution.

    Resolves Bot instances from request tokens.
    Creates and caches Bot instances on-demand. Suitable for multi-tenant applications.
    """

    def __init__(
        self,
        dispatcher: Dispatcher,
        /,
        web_adapter: WebAdapter,
        routing: TokenRouting,
        security: Security | None = None,
        bot_config: BotConfig | None = None,
        handle_in_background: bool = True,
    ) -> None:
        super().__init__(
            dispatcher,
            web_adapter=web_adapter,
            routing=routing,
            security=security,
            handle_in_background=handle_in_background,
        )
        self.routing = routing
        self.bot_config = bot_config or BotConfig()
        self._bots: dict[str, Bot] = {}

    def _get_bot_from_request(self, bound_request: BoundRequest) -> Bot | None:
        """
        Get a :class:`Bot` instance from request by token.

        If the bot is not yet created, it will be created automatically.

        :param bound_request: Incoming request
        :return: Bot instance or None
        """
        token = self.routing.extract_token(bound_request)
        if not token:
            return None
        return self.get_bot(token)

    def get_bot(self, token: str) -> Bot:
        """
        Resolve or create a Bot instance by token and cache it.

        :param token: The bot token
        :return: Bot

        .. note::
            To connect the bot to Telegram API and set up webhook,
            use :meth:`set_webhook`.
        """
        bot = self._bots.get(token)
        if not bot:
            bot = Bot(
                token=token,
                defaults=self.bot_config.defaults,
            )
            self._bots[token] = bot
        return bot

    async def set_webhook(
        self,
        token: str,
        *,
        update_types: list[str] | None = None,
    ) -> Bot:
        """Set the webhook for the Bot instance resolved by token."""
        bot = self.get_bot(token)
        secret_token = None
        if self.security is not None:
            secret_token = await self.security.get_secret_token(bot=bot)

        await bot.subscribe(
            url=self.routing.webhook_point(bot),
            secret=secret_token,
            update_types=update_types,
        )
        return bot

    async def on_startup(
        self,
        app: Any,
        *args: Any,
        bots: set[Bot] | None = None,
        **kwargs: Any,
    ) -> None:
        all_bots = (
            set(bots) | set(self._bots.values()) if bots else set(self._bots.values())
        )
        workflow_data = self._build_workflow_data(app=app, bots=all_bots, **kwargs)
        self.dispatcher.workflow_data.update(workflow_data)

        await self.dispatcher.feed_signal(BeforeStartup())
        await self.dispatcher.feed_signal(AfterStartup())

    async def on_shutdown(self, app: Any, *args: Any, **kwargs: Any) -> None:
        workflow_data = self._build_workflow_data(
            app=app,
            bots=set(self._bots.values()),
            **kwargs,
        )
        self.dispatcher.workflow_data.update(workflow_data)

        await self.dispatcher.feed_signal(BeforeShutdown())

        for bot in self._bots.values():
            await bot.close()
        self._bots.clear()

        await self.dispatcher.feed_signal(AfterShutdown())
