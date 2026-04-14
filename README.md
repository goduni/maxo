<p align="center">
  <a href="https://github.com/K1rl3s/maxo">
    <img width="200px" height="200px" alt="maxo" src="https://raw.githubusercontent.com/K1rL3s/maxo/refs/heads/master/docs/_static/maxo-logo.png">
  </a>
</p>
<h1 align="center">
  maxo
</h1>

<div align="center">

[![License](https://img.shields.io/pypi/l/maxo.svg?style=flat)](https://github.com/K1rL3s/maxo/blob/master/LICENSE)
[![Status](https://img.shields.io/pypi/status/maxo.svg?style=flat)](https://pypi.org/project/maxo/)
[![PyPI](https://img.shields.io/pypi/v/maxo?label=pypi&style=flat)](https://pypi.org/project/maxo/)
[![Downloads](https://img.shields.io/pypi/dm/maxo?style=flat)](https://pypi.org/project/maxo/)
[![GitHub Repo stars](https://img.shields.io/github/stars/K1rL3s/maxo?style=flat)](https://github.com/K1rL3s/maxo/stargazers)
[![Supported python versions](https://img.shields.io/pypi/pyversions/maxo.svg?style=flat)](https://pypi.org/project/maxo/)
[![Docs](https://img.shields.io/readthedocs/maxo?style=flat)](https://maxo.readthedocs.io)
[![Tests](https://img.shields.io/github/actions/workflow/status/K1rL3s/maxo/test.yml?style=flat&label=tests)](https://github.com/K1rL3s/maxo/actions)
[![Coverage](https://codecov.io/gh/K1rL3s/maxo/graph/badge.svg?style=flat)](https://codecov.io/gh/K1rL3s/maxo)

</div>

<p align="center">
    <b>
        Асинхронный фреймворк для разработки <a href="https://dev.max.ru/docs">ботов</a> в <a href="https://max.ru">max.ru</a>
    </b>
</p>

<p align="center">
    <a href="https://maxo.readthedocs.io"><b>Документация</b></a><br><br>
    Интерфейс основан на <a href="https://github.com/aiogram/aiogram">aiogram</a><br>
    <a href="./src/maxo/dialogs">maxo/dialogs</a> сделано из <a href="https://github.com/Tishka17/aiogram_dialog">aiogram_dialog</a><br>
    <a href="./src/maxo/transport/webhook">maxo/transport/webhook</a> сделано из <a href="https://github.com/m-xim/aiogram-webhook">aiogram-webhook</a><br>
</p>

## Установка

Через `pip`:
```commandline
pip install maxo==0.5.3
```

В `pyproject.toml`:
```toml
[project]
dependencies = [
    "maxo==0.5.3",
]
```

## Особенности

- Асинхронность на базе `aiohttp` и [`unihttp`](https://github.com/goduni/unihttp) ([asyncio](https://docs.python.org/3/library/asyncio.html), [PEP 492](https://peps.python.org/pep-0492/))
- 100% покрытие типами, [`adaptix`](https://github.com/reagento/adaptix) для валидации данных
- Роутеры, фильтры, милдвари
- Встроенная машина состояний (FSM) и диалоги поверх них
- Поддержка лонг-поллинга и вебхуков через `aiohttp` и `fastapi`
- Интеграции с `dishka` и `magic_filter`
- Автогенерация методов, типов и апдейтов по [официальной документации](https://dev.max.ru/docs-api)

## Быстрый старт

Больше примеров в [примерах](./examples)

### Эхо-бот

```python
from maxo import Bot, Dispatcher
from maxo.routing.updates import MessageCreated
from maxo.transport.long_polling import LongPolling
from maxo.utils.facades import MessageCreatedFacade

bot = Bot("TOKEN")
dispatcher = Dispatcher()

@dispatcher.message_created()
async def echo_handler(update: MessageCreated, facade: MessageCreatedFacade) -> None:
    text = update.message.body.text or "Текста нет"
    await facade.answer_text(text)

LongPolling(dispatcher).run(bot)
```

### Команды

```python
from maxo import Bot, Dispatcher
from maxo.routing.filters import Command, CommandObject, CommandStart
from maxo.routing.updates import MessageCreated
from maxo.transport.long_polling import LongPolling
from maxo.utils.facades import MessageCreatedFacade

bot = Bot("TOKEN")
dispatcher = Dispatcher()

@dispatcher.message_created(CommandStart())
# или @dispatcher.message_created(Command("start"))
async def start_handler(
    message: MessageCreated,
    command: CommandObject,
    facade: MessageCreatedFacade,
) -> None:
    await facade.answer_text(f"Привет! Я бот. Диплинк: {command.args}")

LongPolling(dispatcher).run(bot)
```

### Клавиатуры

```python
from magic_filter import F

from maxo import Bot, Dispatcher
from maxo.integrations.magic_filter import MagicFilter
from maxo.routing.filters import CommandStart
from maxo.routing.updates import MessageCallback, MessageCreated
from maxo.transport.long_polling import LongPolling
from maxo.utils.builders import KeyboardBuilder
from maxo.utils.facades import MessageCallbackFacade, MessageCreatedFacade

bot = Bot("TOKEN")
dispatcher = Dispatcher()

@dispatcher.message_created(CommandStart())
async def start_handler(message: MessageCreated, facade: MessageCreatedFacade) -> None:
    keyboard = (
        KeyboardBuilder()
        .add_callback(
            text="Колбэк кнопка",
            payload="callback_payload",
        )
        .add_message(text="Текстовая кнопка")
        .add_link(
            text="Maxo",
            url="https://github.com/K1rL3s/maxo",
        )
        .adjust(1, repeat=True)
        .build()
    )
    await facade.answer_text("Кнопочки:", keyboard=keyboard)

@dispatcher.message_callback(MagicFilter(F.payload == "callback_payload"))
async def button_handler(
    callback: MessageCallback,
    facade: MessageCallbackFacade,
) -> None:
    await facade.callback_answer("Вы нажали на кнопку!")

LongPolling(dispatcher).run(bot)
```

### Вебхук

```python
import logging
import os

from aiohttp import web

from maxo import Bot, Dispatcher, Router
from maxo.enums import TextFormat
from maxo.routing.updates import BotStarted, MessageCreated
from maxo.routing.utils import collect_used_updates
from maxo.transport.webhook.adapters.aiohttp import AiohttpWebAdapter
from maxo.transport.webhook.engines import SimpleEngine, WebhookEngine
from maxo.transport.webhook.routing import StaticRouting
from maxo.transport.webhook.security import Security, StaticSecretToken
from maxo.utils.facades import BotStartedFacade, MessageCreatedFacade

bot = Bot(os.environ["TOKEN"])
router = Router()

@router.bot_started()
async def start_handler(bot_started: BotStarted, facade: BotStartedFacade) -> None:
    await facade.send_message(text=f"Привет из вебхука, {bot_started.user.first_name}!")

@router.message_created()
async def echo_handler(message: MessageCreated, facade: MessageCreatedFacade) -> None:
    await facade.answer_text(
        text=message.message.body.html_text,
        format=TextFormat.HTML,
    )

@router.after_startup()
async def on_startup(dispatcher: Dispatcher, webhook_engine: WebhookEngine) -> None:
    await webhook_engine.set_webhook(update_types=collect_used_updates(dispatcher))

def main() -> None:
    dispatcher = Dispatcher()
    dispatcher.include(router)

    engine = SimpleEngine(
        dispatcher,
        bot,
        web_adapter=AiohttpWebAdapter(),
        routing=StaticRouting(url="https://example.com/webhook"),
        security=Security(secret_token=StaticSecretToken("pepa_pig")),
    )
    app = web.Application()
    engine.register(app)

    web.run_app(app, host="127.0.0.1", port=8080)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    main()
```

## Связь
Если у вас есть вопросы, вы можете задать их в Телеграме [\@maxo_py](https://t.me/maxo_py) или [Максе](https://max.ru/join/rwJmWA4B5AipBiJdWRkORGjxFmqnJPUhJbQxxmscrnc)

