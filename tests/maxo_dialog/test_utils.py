from datetime import UTC, datetime

from maxo.dialogs.api.internal import FakeRecipient, FakeUser
from maxo.dialogs.utils import is_recipient_loaded, is_user_loaded
from maxo.enums import ChatType
from maxo.types import Recipient, User


def test_is_recipient_loaded() -> None:
    assert is_recipient_loaded(
        Recipient(chat_id=1, user_id=1, chat_type=ChatType.DIALOG)
    )
    assert not is_recipient_loaded(
        FakeRecipient(chat_id=1, user_id=1, chat_type=ChatType.DIALOG)
    )


def test_is_user_loaded() -> None:
    assert is_user_loaded(
        User(
            user_id=1,
            is_bot=False,
            first_name="",
            last_activity_time=datetime.fromtimestamp(1234567890, tz=UTC),
        )
    )
    assert not is_user_loaded(
        FakeUser(
            user_id=1,
            is_bot=False,
            first_name="",
            last_activity_time=datetime.fromtimestamp(1234567890, tz=UTC),
        )
    )
