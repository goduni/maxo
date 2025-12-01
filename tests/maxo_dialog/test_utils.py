from aiogram.types import User

from maxo.dialogs.api.internal import FakeRecipient, FakeUser
from maxo.dialogs.utils import is_recipient_loaded, is_user_loaded
from maxo.enums import ChatType
from maxo.types import Recipient


def test_is_recipient_loaded():
    assert is_recipient_loaded(Recipient(chat_id=1, user_id=1, type=ChatType.DIALOG))
    assert not is_recipient_loaded(
        FakeRecipient(chat_id=1, user_id=1, type=ChatType.DIALOG),
    )


def test_is_user_loaded():
    assert is_user_loaded(User(id=1, is_bot=False, first_name=""))
    assert not is_user_loaded(FakeUser(id=1, is_bot=False, first_name=""))
