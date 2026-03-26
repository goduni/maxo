Сигналы
=======

Сигналы - это события жизненного цикла бота, которые позволяют выполнять код
на определённых этапах запуска и остановки. В отличие от обновлений (updates),
сигналы генерируются самим фреймворком, а не приходят от API MAX.ru.


Доступные сигналы
-----------------

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Сигнал
     - Когда вызывается
   * - ``BeforeStartup``
     - **До** начала поллинга. Бот ещё не подключён к API. Здесь фреймворк валидирует граф роутеров, резолвит middleware и переводит роутеры в состояние «запущен».
   * - ``AfterStartup``
     - **После** подключения бота к API, но **до** получения первого обновления. Бот уже авторизован, можно отправлять сообщения.
   * - ``BeforeShutdown``
     - **До** закрытия соединения с API. Бот ещё активен, можно отправлять прощальные сообщения.
   * - ``AfterShutdown``
     - **После** закрытия соединения. Бот отключён, соединение закрыто.


Порядок вызова
--------------

При запуске через ``LongPolling`` сигналы вызываются в следующем порядке:

.. code-block:: text

    BeforeStartup          ← валидация, резолв middleware
        ↓
    бот подключается к API
        ↓
    AfterStartup           ← бот готов к работе
        ↓
    ... обработка обновлений ...
        ↓
    BeforeShutdown         ← бот ещё активен
        ↓
    бот отключается от API
        ↓
    AfterShutdown          ← всё завершено


Регистрация обработчиков
------------------------

Обработчики сигналов регистрируются через одноимённые атрибуты роутера или диспетчера.
Можно использовать как декоратор, так и метод ``handler()``.

Через декоратор
~~~~~~~~~~~~~~~

.. code-block:: python

    from maxo import Bot, Dispatcher
    from maxo.transport.long_polling import LongPolling

    dispatcher = Dispatcher()

    @dispatcher.after_startup()
    async def on_startup(bot: Bot) -> None:
        info = bot.state.info
        print(f"Бот @{info.username} запущен!")

    @dispatcher.before_shutdown()
    async def on_shutdown(bot: Bot) -> None:
        print("Бот останавливается...")

    LongPolling(dispatcher).run(Bot("TOKEN"))


Через метод ``handler()``
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    async def on_startup(bot: Bot) -> None:
        print(f"Бот @{bot.state.info.username} запущен!")

    dispatcher.after_startup.handler(on_startup)


Сигналы в дочерних роутерах
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Сигналы поддерживаются не только в ``Dispatcher``, но и в обычных ``Router``.
При запуске фреймворк обходит всё дерево роутеров и вызывает обработчики
сигналов на каждом уровне:

.. code-block:: python

    from maxo import Bot, Dispatcher, Router
    from maxo.transport.long_polling import LongPolling

    router = Router()

    @router.after_startup()
    async def on_router_startup(bot: Bot) -> None:
        print("Роутер готов к работе")

    @router.before_shutdown()
    async def on_router_shutdown() -> None:
        print("Роутер завершает работу")

    dispatcher = Dispatcher()
    dispatcher.include(router)
    LongPolling(dispatcher).run(Bot("TOKEN"))


Типичные сценарии
-----------------

Инициализация ресурсов
~~~~~~~~~~~~~~~~~~~~~~

Открытие соединений к базам данных, кэшам или внешним сервисам:

.. code-block:: python

    import redis.asyncio as redis

    @dispatcher.after_startup()
    async def setup_redis() -> None:
        pool = redis.ConnectionPool.from_url("redis://localhost")
        dispatcher.workflow_data["redis"] = redis.Redis(connection_pool=pool)

    @dispatcher.before_shutdown()
    async def close_redis() -> None:
        r = dispatcher.workflow_data.get("redis")
        if r is not None:
            await r.aclose()


Уведомление администратора
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    ADMIN_USER_ID = 123456

    @dispatcher.after_startup()
    async def notify_admin(bot: Bot) -> None:
        await bot.send_message(user_id=ADMIN_USER_ID, text="Бот запущен!")

    @dispatcher.before_shutdown()
    async def notify_admin_shutdown(bot: Bot) -> None:
        await bot.send_message(user_id=ADMIN_USER_ID, text="Бот останавливается.")


Внедрение зависимостей (``workflow_data``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Данные, помещённые в ``dispatcher.workflow_data`` в обработчике сигнала,
будут доступны во всех обработчиках обновлений через контекст (``Ctx``):

.. code-block:: python

    @dispatcher.after_startup()
    async def setup_config() -> None:
        dispatcher.workflow_data["admin_ids"] = [123, 456, 789]

    @dispatcher.message_created()
    async def handler(update, facade, admin_ids: list[int]) -> None:
        if update.message.sender.user_id in admin_ids:
            await facade.answer_text("Привет, админ!")


Отличие от обработчиков обновлений
-----------------------------------

.. list-table::
   :header-rows: 1
   :widths: 35 35 30

   * - Свойство
     - Обработчик обновления
     - Обработчик сигнала
   * - Источник события
     - API MAX.ru
     - Фреймворк
   * - Вызывается
     - При каждом обновлении
     - Один раз (при старте / остановке)
   * - Первый совпавший
     - Да, только первый обработчик
     - Нет, **все** зарегистрированные обработчики
   * - Доступ к ``bot``
     - Всегда
     - ``AfterStartup`` и ``BeforeShutdown`` - да; ``BeforeStartup`` и ``AfterShutdown`` - нет (бот ещё / уже не подключён)
