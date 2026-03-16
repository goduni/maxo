from maxo.enums import TextFormat
from maxo.types import MaxoType


class BotDefaults(MaxoType):
    """Default values for bot API calls."""

    text_format: TextFormat | None = None
    """Default text format for messages"""
    disable_link_preview: bool | None = None
    """Default value for disable_link_preview parameter"""
