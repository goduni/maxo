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
        Асинхронный фреймворк для разработки <a href="https://dev.max.ru/docs">ботов</a> из <a href="https://max.ru">max.ru</a>
    </b>
</p>

<p align="center">
    <a href="https://maxo.readthedocs.io">Документация</a><br><br>
    <a href="https://github.com/IvanKirpichnikov/maxo">Оригинальный репозиторий</a><br>
    <a href="./src/maxo/dialogs">maxo/dialogs</a> переделаны из <a href="https://github.com/Tishka17/aiogram_dialog">aiogram_dialog</a>
</p>

## Установка

Через `pip`:
```commandline
pip install maxo==0.3.0
```

В `pyproject.toml`:
```toml
[project]
dependencies = [
    "maxo==0.3.0",
]
```

## Быстрый старт

Больше примеров в [примерах](./examples)

### Эхо-бот

```python
import logging
import os

from maxo import Bot, Dispatcher
from maxo.routing.updates.message_created import MessageCreated
from maxo.utils.facades.updates.message_created import MessageCreatedFacade
from maxo.utils.long_polling import LongPolling

bot = Bot(os.environ["TOKEN"])
dispatcher = Dispatcher()

@dispatcher.message_created()
async def echo_handler(update: MessageCreated, facade: MessageCreatedFacade) -> None:
    text = update.message.body.text or "Текста нет"
    await facade.answer_text(text)

logging.basicConfig(level=logging.INFO)
LongPolling(dispatcher).run(bot)
```

### Команды

```python
import logging
import os

from maxo import Bot, Dispatcher, Router
from maxo.routing.filters import CommandStart
from maxo.routing.updates.message_created import MessageCreated
from maxo.utils.facades import MessageCreatedFacade
from maxo.utils.long_polling import LongPolling

bot = Bot(os.environ["TOKEN"])
router = Router()

@router.message_created(CommandStart())
# или @router.message_created(Command("start"))
async def start_handler(update: MessageCreated, facade: MessageCreatedFacade) -> None:
    await facade.answer_text("Привет! Я бот")

def main():
    logging.basicConfig(level=logging.INFO)
    dispatcher = Dispatcher()
    dispatcher.include(router)
    LongPolling(dispatcher).run(bot)

if __name__ == "__main__":
    main()
```

### Клавиатура

```python
import logging
import os

from magic_filter import F

from maxo import Bot, Dispatcher, Router
from maxo.integrations.magic_filter import MagicFilter
from maxo.routing.filters import CommandStart
from maxo.routing.updates import MessageCreated, MessageCallback
from maxo.utils.builders import KeyboardBuilder
from maxo.utils.facades import MessageCallbackFacade, MessageCreatedFacade
from maxo.utils.long_polling import LongPolling

bot = Bot(os.environ["TOKEN"])
router = Router()

@router.message_created(CommandStart())
async def start_handler(
    update: MessageCreated,
    facade: MessageCreatedFacade,
) -> None:
    keyboard = (
        KeyboardBuilder()
        .add_callback(
            text="Нажми меня",
            payload="my_callback",
        )
        .build()
    )
    await facade.answer_text(
        "Это сообщение с клавиатурой:",
        keyboard=keyboard,
    )

@router.message_callback(MagicFilter(F.payload == "my_callback"))
async def button_handler(
    update: MessageCallback,
    facade: MessageCallbackFacade,
    bot: Bot,
) -> None:
    await facade.callback_answer("Вы нажали на кнопку!")
    await bot.send_message(
        user_id=update.user.user_id,
        text="Вы нажали на кнопку!",
    )

def main():
    logging.basicConfig(level=logging.INFO)
    dispatcher = Dispatcher()
    dispatcher.include(router)
    LongPolling(dispatcher).run(bot)

if __name__ == "__main__":
    main()
```

## Связь
Если у вас есть вопросы, вы можете задать их в Телеграме [\@maxo_py](https://t.me/maxo_py) или [Максе](https://max.ru/join/rwJmWA4B5AipBiJdWRkORGjxFmqnJPUhJbQxxmscrnc)

