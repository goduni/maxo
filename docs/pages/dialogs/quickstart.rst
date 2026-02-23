=============
Быстрый старт
=============

Чтобы начать использовать ``maxo.dialogs``, давайте создадим простое эхо-меню с кнопкой.

Подготовка состояний
====================

Каждое окно в диалоге привязывается к состоянию из ``StatesGroup``.

.. code-block:: python

    from maxo.fsm import State, StatesGroup

    class MyDialog(StatesGroup):
        main = State()

Создание окна и диалога
=======================

Окно содержит элементы UI (виджеты). Соберем диалог из одного окна:

.. code-block:: python

    from maxo.dialogs import Window, Dialog
    from maxo.dialogs.widgets.kbd import Button
    from maxo.dialogs.widgets.text import Const
    from maxo.dialogs.api.protocols import DialogManager
    from maxo.types import MessageCallback
    from maxo.dialogs.api.entities import CancelEventProcessing

    async def on_click(callback: MessageCallback, button: Button, manager: DialogManager):
        await callback.answer("Клик!")

    dialog = Dialog(
        Window(
            Const("Привет! Это твой первый диалог на maxo.dialogs."),
            Button(Const("Нажми меня"), id="btn1", on_click=on_click),
            state=MyDialog.main,
        ),
    )

Точка входа
===========

Теперь нам нужен хэндлер (например, на команду ``/start``), который запустит диалог. Чтобы запустить диалог, используйте метод ``start()`` у ``DialogManager``:

.. code-block:: python

    from maxo import Router
    from maxo.dialogs.api.protocols import DialogManager
    from maxo.dialogs import StartMode
    from maxo.types.message import MessageCreated

    router = Router()

    @router.message_created(Command("start"))
    async def start_handler(message: MessageCreated, dialog_manager: DialogManager):
        await dialog_manager.start(MyDialog.main, mode=StartMode.RESET_STACK)

Регистрация в приложении
========================

Осталось только собрать всё вместе и зарегистрировать систему диалогов в корневом роутере. Вызовите ``setup_dialogs(dp)``.

.. code-block:: python

    import anyio
    from maxo import Bot, Dispatcher, Router
    from maxo.dialogs import setup_dialogs

    async def main():
        bot = Bot("YOUR_BOT_TOKEN")
        dp = Dispatcher()

        # Подключаем роутер с хэндлером и роутер (диалог)
        dp.include_router(router)
        dp.include_router(dialog)

        # Важно! Инициализируем систему диалогов
        setup_dialogs(dp)

        await dp.start_polling(bot)

    if __name__ == "__main__":
        anyio.run(main)
