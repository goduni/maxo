from unittest.mock import MagicMock, Mock

import pytest

from maxo.dialogs import DialogManager
from maxo.dialogs.api.entities import Context
from maxo.fsm.state import State


@pytest.fixture
def mock_manager() -> DialogManager:
    manager = MagicMock()
    context = Context(
        dialog_data={},
        start_data={},
        widget_data={},
        state=State(),
        _stack_id="_stack_id",
        _intent_id="_intent_id",
    )
    manager.current_context = Mock(side_effect=lambda: context)
    manager.is_preview = MagicMock(return_value=False)
    return manager
