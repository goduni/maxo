from maxo.omit import Omittable, Omitted
from maxo.types.button import Button


class ChatButton(Button):
    """
    Кнопка, которая создает новый чат, как только первый пользователь на нее нажмёт.
    BБот будет добавлен в участники чата как администратор.
    MАвтор сообщения станет владельцем чата.

    Args:
        chat_description: Описание чата
        chat_title: Название чата, который будет создан
        start_payload: Стартовая полезная нагрузка будет отправлена боту, как только чат будет создан
        uuid: Уникальный ID кнопки среди всех кнопок чата на клавиатуре.
            Если `uuid` изменён, новый чат будет создан при следующем нажатии.
            Сервер сгенерирует его в момент, когда кнопка будет впервые размещена.
            Используйте его при редактировании сообщения.'
    """

    chat_title: str

    chat_description: Omittable[str | None] = Omitted()
    start_payload: Omittable[str | None] = Omitted()
    uuid: Omittable[int | None] = Omitted()
