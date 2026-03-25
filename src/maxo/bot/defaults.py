from maxo.enums import TextFormat
from maxo.omit import Omittable, Omitted
from maxo.types import MaxoType


class BotDefaults(MaxoType):
    """Default values for bot API calls."""

    text_format: TextFormat | None = None
    """Default text format for messages"""
    disable_link_preview: Omittable[bool | None] = Omitted()
    """Default value for disable_link_preview parameter"""

    def __post_init__(self) -> None:
        # API ожидает Omittable[bool]. None здесь для совместимости с maxo 0.5.0
        if self.disable_link_preview is None:
            self.disable_link_preview = Omitted()
