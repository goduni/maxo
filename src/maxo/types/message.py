from datetime import datetime

from maxo.errors import AttributeIsEmptyError
from maxo.omit import Omittable, Omitted, is_defined
from maxo.types.base import MaxoType
from maxo.types.linked_message import LinkedMessage
from maxo.types.message_body import MessageBody
from maxo.types.message_stat import MessageStat
from maxo.types.recipient import Recipient
from maxo.types.user import User


class Message(MaxoType):
    """
    Сообщение в чате

    Args:
        body: Содержимое сообщения. Текст + вложения. Может быть `null`, если сообщение содержит только пересланное сообщение
        link: Пересланное или ответное сообщение
        recipient: Получатель сообщения. Может быть пользователем или чатом
        sender: Пользователь, отправивший сообщение
        stat: Статистика сообщения.
        timestamp: Время создания сообщения в формате Unix-time
        url: Публичная ссылка на пост в канале. Отсутствует для диалогов и групповых чатов
    """

    body: MessageBody
    recipient: Recipient
    timestamp: datetime

    link: Omittable[LinkedMessage | None] = Omitted()
    sender: Omittable[User] = Omitted()
    stat: Omittable[MessageStat | None] = Omitted()
    url: Omittable[str | None] = Omitted()

    @property
    def unsafe_link(self) -> LinkedMessage:
        if is_defined(self.link):
            return self.link

        raise AttributeIsEmptyError(
            obj=self,
            attr="link",
        )

    @property
    def unsafe_body(self) -> MessageBody:
        if is_defined(self.body):
            return self.body

        raise AttributeIsEmptyError(
            obj=self,
            attr="body",
        )

    @property
    def unsafe_stat(self) -> MessageStat:
        if is_defined(self.stat):
            return self.stat

        raise AttributeIsEmptyError(
            obj=self,
            attr="stat",
        )
