from maxo.bot.methods.base import MaxoMethod
from maxo.bot.methods.markers import Body, Query
from maxo.enums.text_format import TextFormat
from maxo.omit import Omittable, Omitted
from maxo.types import Attachments, AttachmentsRequests
from maxo.types.new_message_link import NewMessageLink
from maxo.types.simple_query_result import SimpleQueryResult


class EditMessage(MaxoMethod[SimpleQueryResult]):
    """
    Редактировать сообщение

    Редактирует сообщение в чате. Если поле `attachments` равно `null`, вложения текущего сообщения не изменяются. Если в этом поле передан пустой список, все вложения будут удалены

    >  С помощью метода можно отредактировать сообщения, которые отправлены менее 24 часов назад

    Пример запроса:
    ```bash
    curl -X PUT "https://platform-api.max.ru/messages?message_id=message_id" \
      -H "Authorization: {access_token}" \
      -H "Content-Type: application/json" \
      -d '{
      "text": "Изменённый текст"
    }'
    ```

    Args:
        attachments: Вложения сообщения. Если пусто, все вложения будут удалены
        format: Если установлен, текст сообщения будет форматирован данным способом. Для подробной информации загляните в раздел [Форматирование](/docs-api#Форматирование%20текста)
        link: Ссылка на сообщение
        message_id: ID редактируемого сообщения
        notify: Если false, участники чата не будут уведомлены (по умолчанию `true`)
        text: Новый текст сообщения

    Источник: https://dev.max.ru/docs-api/methods/PUT/messages
    """

    __url__ = "messages"
    __method__ = "put"

    message_id: Query[str]
    """ID редактируемого сообщения"""

    attachments: Body[list[AttachmentsRequests | Attachments] | None] = None
    """Вложения сообщения. Если пусто, все вложения будут удалены"""
    link: Body[NewMessageLink | None] = None
    """Ссылка на сообщение"""
    text: Body[str | None] = None
    """Новый текст сообщения"""
    format: Body[Omittable[TextFormat | None]] = Omitted()
    """Если установлен, текст сообщения будет форматирован данным способом. Для подробной информации загляните в раздел [Форматирование](/docs-api#Форматирование%20текста)"""
    notify: Body[Omittable[bool]] = Omitted()
    """Если false, участники чата не будут уведомлены (по умолчанию `true`)"""
