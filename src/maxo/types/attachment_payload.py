from maxo.types.base import MaxoType


class AttachmentPayload(MaxoType):
    """
    Args:
        url: URL медиа-вложения. Этот URL будет получен в объекте [Update](https://dev.max.ru/docs-api/objects/Update) после отправки сообщения в чат.
            Прямую ссылку на видео также можно получить с помощью метода [`GET /videos/{-videoToken-}`](https://dev.max.ru/docs-api/methods/GET/videos/-videoToken-)
    """

    url: str
