from maxo.types.base import MaxoType
from maxo.types.buttons import InlineButtons


class InlineKeyboardAttachmentRequestPayload(MaxoType):
    """
    Args:
        buttons: Двумерный массив кнопок
    """

    buttons: list[list[InlineButtons]]
