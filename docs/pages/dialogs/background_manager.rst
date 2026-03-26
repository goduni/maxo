==================
Background Manager
==================

В обработчиках ``DialogManager`` передается в качестве аргумента автоматически.
Иногда нужно обновить диалог **из фоновой задачи** - по таймеру, по событию из Redis/Celery/Taskiq, или из стороннего сервиса.

Для этого используется ``BgManagerFactory``.

BgManagerFactory
================

Фабрика автоматически доступна через DI. С её помощью можно получить менеджер для конкретного чата и пользователя:

.. code-block:: python

    from maxo import Bot
    from maxo.dialogs.api.protocols import BgManagerFactory

    async def background_job(bg_factory: BgManagerFactory, bot: Bot, chat_id: int, user_id: int):
        manager = bg_factory.bg(bot=bot, chat_id=chat_id, user_id=user_id)

        # Запуск нового диалога
        await manager.start(SG.main)

        # Или просто обновление UI текущего диалога
        await manager.update({"status": "completed"})

.. note::

   При использовании ``BgManagerFactory`` убедитесь, что ``Dispatcher`` инициализирован с ``KeyBuilder(with_destiny=True)`` - это необходимо для корректной работы системы диалогов.
   Подробнее: `issue #34 <https://github.com/K1rL3s/maxo/issues/34>`_.

Пример: обновление диалога по расписанию
========================================

Представим, что нужно каждую секунду обновлять значение счётчика в диалоге (например, таймер или прогресс загрузки).

.. code-block:: python

    import anyio
    from typing import Any

    from maxo import Bot
    from maxo.dialogs import Dialog, Window
    from maxo.dialogs.widgets.text import Const, Format
    from maxo.dialogs.widgets.kbd import Button
    from maxo.dialogs.api.protocols import BgManagerFactory, DialogManager
    from maxo.routing.updates import MessageCallback
    from maxo.fsm import State, StatesGroup

    class TimerSG(StatesGroup):
        running = State()

    async def timer_getter(dialog_manager: DialogManager, **__: Any) -> dict:
        count = dialog_manager.dialog_data.get("count", 0)
        return {"count": count}

    async def on_start_timer(callback: MessageCallback, button: Button, manager: DialogManager):
        """Запускает фоновую задачу, которая обновляет счётчик."""
        manager.dialog_data["count"] = 0

        bg_factory: BgManagerFactory = manager.middleware_data["dialog_bg_factory"]
        bot: Bot = manager.middleware_data["bot"]
        chat_id = manager.event.chat_id
        user_id = manager.event.user_id

        async def tick() -> None:
            bg = bg_factory.bg(bot=bot, chat_id=chat_id, user_id=user_id)
            for i in range(1, 11):
                await anyio.sleep(1)
                await bg.update({"count": i})

        # Запускаем задачу через TaskGroup, зарегистрированную при старте приложения:
        manager.middleware_data["task_group"].start_soon(tick)
        # Альтернатива (только для asyncio-бэкенда):
        # import asyncio; asyncio.create_task(tick())

    timer_dialog = Dialog(
        Window(
            Format("Счётчик: {count}"),
            Button(Const("Старт"), id="start", on_click=on_start_timer),
            state=TimerSG.running,
            getter=timer_getter,
        ),
    )
