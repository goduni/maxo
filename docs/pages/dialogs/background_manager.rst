==================
Background Manager
==================

В обычных хэндлерах и колбеках ``DialogManager`` передается в качестве аргумента автоматически.
Но иногда вам нужно обновить диалог **из фоновой задачи** — по таймеру, по событию из Redis/Celery/Taskiq, или из стороннего сервиса.

Для этого используется ``BgManagerFactory``.

BgManagerFactory
================

Фабрика автоматически доступна через DI. С её помощью можно получить менеджер для конкретного чата и пользователя:

.. code-block:: python

    from maxo.dialogs.api.protocols import BgManagerFactory

    async def background_job(bg_factory: BgManagerFactory, chat_id: int, user_id: int):
        manager = bg_factory.bg(chat_id=chat_id, user_id=user_id)

        # Запуск нового диалога
        await manager.start(SG.main)

        # Или просто обновление UI текущего диалога
        await manager.update({"status": "completed"})

Пример: обновление диалога по расписанию
========================================

Представим, что нужно каждую секунду обновлять значение счётчика в диалоге (например, таймер или прогресс загрузки).

.. code-block:: python

    import anyio
    from maxo.dialogs import Dialog, Window
    from maxo.dialogs.widgets.text import Format
    from maxo.dialogs.widgets.kbd import Button
    from maxo.dialogs.api.protocols import BgManagerFactory
    from maxo.fsm import State, StatesGroup

    class TimerSG(StatesGroup):
        running = State()

    async def timer_getter(dialog_manager, **kwargs):
        count = dialog_manager.dialog_data.get("count", 0)
        return {"count": count}

    async def on_start_timer(callback, button, manager):
        """Запускает фоновую задачу, которая обновляет счётчик."""
        manager.dialog_data["count"] = 0

        bg_factory: BgManagerFactory = manager.middleware_data["bg_factory"]
        chat_id = manager.event.chat_id
        user_id = manager.event.user_id

        async def tick():
            bg = bg_factory.bg(chat_id=chat_id, user_id=user_id)
            for i in range(1, 11):
                await anyio.sleep(1)
                await bg.update({"count": i})

        # Запускаем задачу в фоне
        manager.middleware_data["task_group"].start_soon(tick)

    timer_dialog = Dialog(
        Window(
            Format("Счётчик: {count}"),
            Button(Const("Старт"), id="start", on_click=on_start_timer),
            state=TimerSG.running,
            getter=timer_getter,
        ),
    )
