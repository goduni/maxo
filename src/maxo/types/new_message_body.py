from maxo.enums.text_format import TextFormat
from maxo.omit import Omittable, Omitted
from maxo.types.attachments import AttachmentsRequests
from maxo.types.base import MaxoType
from maxo.types.new_message_link import NewMessageLink


class NewMessageBody(MaxoType):
    """
    Args:
        attachments: Вложения сообщения. Если пусто, все вложения будут удалены
        format: Если установлен, текст сообщения будет форматирован данным способом. Для подробной информации загляните в раздел [Форматирование](/docs-api#Форматирование%20текста)
        link: Ссылка на сообщение
        notify: Если false, участники чата не будут уведомлены (по умолчанию `true`)
        text: Новый текст сообщения
    """

    attachments: list[AttachmentsRequests] | None = None
    link: NewMessageLink | None = None
    text: str | None = None

    format: Omittable[TextFormat | None] = Omitted()
    notify: Omittable[bool] = Omitted()
