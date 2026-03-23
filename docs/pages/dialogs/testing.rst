:orphan:

======================
Тестирование диалогов
======================

Пакет ``maxo.dialogs.test_tools`` позволяет тестировать диалоги без реального API
VK Max и без подключения к сети. Тесты выполняются быстро и детерминировано:
бот работает в памяти, а отправленные сообщения перехватываются для проверки.

Используйте этот подход на уровне интеграционных тестов: реальная бизнес-логика
и опционально реальная БД, но без Telegram/Max.

Компоненты
==========

``JsonMemoryStorage``
---------------------

Реализация FSM-хранилища в памяти. Заменяет Redis в тестах — состояния диалогов
хранятся в словаре и не требуют внешних зависимостей.

.. code-block:: python

    from maxo.dialogs.test_tools.memory_storage import JsonMemoryStorage

    storage = JsonMemoryStorage()

``BotClient``
-------------

Симулятор пользователя. Позволяет отправлять текстовые сообщения и нажимать кнопки
без реального подключения к API.

.. code-block:: python

    from maxo.dialogs.test_tools import BotClient

    client = BotClient(dp, user_id=1, chat_id=1)

``MockMessageManager``
----------------------

Перехватывает исходящие сообщения бота. Вместо отправки через API сохраняет их
во внутренний список — вы можете прочитать их и проверить содержимое.

.. code-block:: python

    from maxo.dialogs.test_tools import MockMessageManager

    message_manager = MockMessageManager()

Настройка окружения
===================

Соберите ``Dispatcher`` с ``JsonMemoryStorage`` и передайте ``MockMessageManager``
в ``setup_dialogs()``. ``DefaultKeyBuilder(with_destiny=True)`` обязателен
для корректной работы диалогов.

.. code-block:: python

    from maxo import Dispatcher
    from maxo.dialogs import setup_dialogs
    from maxo.dialogs.test_tools import BotClient, MockMessageManager
    from maxo.dialogs.test_tools.memory_storage import JsonMemoryStorage
    from maxo.fsm.key_builder import DefaultKeyBuilder

    storage = JsonMemoryStorage()
    message_manager = MockMessageManager()

    dp = Dispatcher(
        storage=storage,
        key_builder=DefaultKeyBuilder(with_destiny=True),
    )
    dp.include(my_dialog)
    setup_dialogs(dp, message_manager=message_manager)

    client = BotClient(dp)

Проверка рендеринга окна
========================

Отправьте команду и прочитайте последнее сообщение из ``MockMessageManager``.
Текст доступен через ``msg.body.text``, кнопки — через ``msg.body.keyboard.buttons``.

.. code-block:: python

    await client.send("/start")

    msg = message_manager.last_message()
    assert "Главное меню" in msg.body.text

    # Проверка кнопок
    buttons = [btn.text for row in msg.body.keyboard.buttons for btn in row]
    assert "Подробнее" in buttons

Используйте ``reset_history()`` чтобы очистить историю между шагами теста —
так вы точно читаете сообщение от нужного действия:

.. code-block:: python

    await client.send("/start")
    message_manager.reset_history()   # очищаем — дальше только новые сообщения

    await client.click(msg, locator)
    detail_msg = message_manager.last_message()

Локаторы кнопок
===============

``BotClient.click()`` принимает локатор — объект, который находит нужную кнопку
в сообщении.

``InlineButtonTextLocator``
---------------------------

Ищет кнопку по тексту (поддерживает регулярные выражения).

.. code-block:: python

    from maxo.dialogs.test_tools.keyboard import InlineButtonTextLocator

    # Точное совпадение
    locator = InlineButtonTextLocator("Подробнее")

    # Regex: любая кнопка с эмодзи-флагом
    locator = InlineButtonTextLocator(r"🇷🇺.*")

``InlineButtonPositionLocator``
--------------------------------

Ищет кнопку по позиции в клавиатуре (нумерация с 0).

.. code-block:: python

    from maxo.dialogs.test_tools.keyboard import InlineButtonPositionLocator

    # Первая кнопка в первом ряду
    locator = InlineButtonPositionLocator(row=0, column=0)

``InlineButtonDataLocator``
----------------------------

Ищет кнопку по значению callback-payload (поддерживает регулярные выражения).

.. code-block:: python

    from maxo.dialogs.test_tools.keyboard import InlineButtonDataLocator

    locator = InlineButtonDataLocator(r"action:detail:\d+")

Проверка переходов
==================

Нажатие кнопки возвращает ``callback_id``. Передайте его в ``assert_answered()``
чтобы убедиться, что бот ответил на callback (без ответа у пользователя
останется «часы» на кнопке).

.. code-block:: python

    await client.send("/start")
    menu_msg = message_manager.last_message()
    message_manager.reset_history()

    callback_id = await client.click(menu_msg, InlineButtonTextLocator("Подробнее"))
    message_manager.assert_answered(callback_id)

    detail_msg = message_manager.last_message()
    assert "Детальная страница" in detail_msg.body.text

Паттерны pytest
===============

Выносите создание окружения в фикстуры pytest чтобы изолировать каждый тест.
Используйте ``autouse=True`` чтобы автоматически очищать историю.

.. code-block:: python

    import pytest
    import pytest_asyncio
    from maxo import Dispatcher
    from maxo.dialogs import setup_dialogs
    from maxo.dialogs.test_tools import BotClient, MockMessageManager
    from maxo.dialogs.test_tools.memory_storage import JsonMemoryStorage
    from maxo.fsm.key_builder import DefaultKeyBuilder

    @pytest_asyncio.fixture(scope="session")
    async def dp() -> Dispatcher:
        storage = JsonMemoryStorage()
        _dp = Dispatcher(
            storage=storage,
            key_builder=DefaultKeyBuilder(with_destiny=True),
        )
        _dp.include(my_dialog)
        return _dp

    @pytest_asyncio.fixture(scope="session")
    async def message_manager(dp: Dispatcher) -> MockMessageManager:
        mm = MockMessageManager()
        setup_dialogs(dp, message_manager=mm)
        return mm

    @pytest_asyncio.fixture(scope="session")
    async def client(dp: Dispatcher) -> BotClient:
        return BotClient(dp)

    @pytest.fixture(autouse=True)
    def reset(message_manager: MockMessageManager):
        message_manager.reset_history()
        yield
        message_manager.reset_history()

    @pytest.mark.asyncio
    async def test_main_menu(client: BotClient, message_manager: MockMessageManager):
        await client.send("/start")
        msg = message_manager.last_message()
        assert "Главное меню" in msg.body.text

Полный пример
=============

Рабочий пример с обоими сценариями (рендеринг окна и переход по кнопке):
:download:`examples/dialogs_testing.py <../../../examples/dialogs_testing.py>`
