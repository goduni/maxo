import pytest

from maxo.bot.defaults import BotDefaults
from maxo.bot.methods import EditMessage, SendMessage
from maxo.enums import TextFormat
from maxo.omit import Omittable, Omitted, is_omitted
from maxo.serialization import create_retort
from maxo.types import NewMessageBody


@pytest.mark.parametrize(
    "default",
    [TextFormat.HTML, TextFormat.MARKDOWN, None, Omitted()],
)
def test_bot_default_text_format(default: Omittable[TextFormat | None]) -> None:
    defaults = BotDefaults(text_format=default)
    retort = create_retort(defaults=defaults, warming_up=False)

    data = retort.dump(SendMessage())
    if is_omitted(default):
        assert "format" not in data["body"]
    else:
        assert data["body"]["format"] == default

    data = retort.dump(EditMessage(message_id="1"))
    if is_omitted(default):
        assert "format" not in data["body"]
    else:
        assert data["body"]["format"] == default

    data = retort.dump(NewMessageBody())
    if is_omitted(default):
        assert "format" not in data
    else:
        assert data["format"] == default


@pytest.mark.parametrize(
    "default",
    [True, False, Omitted()],
)
def test_bot_default_disable_link_preview(default: Omittable[bool]):
    defaults = BotDefaults(disable_link_preview=default)
    retort = create_retort(defaults=defaults, warming_up=False)

    data = retort.dump(SendMessage())
    if is_omitted(default):
        assert "disable_link_preview" not in data["query"]
    else:
        assert data["query"]["disable_link_preview"] == default
