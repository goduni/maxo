import pytest

from maxo.dialogs import DialogManager
from maxo.dialogs.widgets.kbd import ListGroup
from maxo.dialogs.widgets.kbd.button import Button, Url
from maxo.dialogs.widgets.text import Const, Format


@pytest.mark.asyncio
async def test_render_list_group_with_url_button(mock_manager: DialogManager) -> None:
    list_group = ListGroup(
        Url(Const("Url"), url=Const("https://test.com")),
        id="list",
        items=["a", "b", "c"],
        item_id_getter=lambda item: item,
    )

    keyboard = await list_group.render_keyboard(data={}, manager=mock_manager)

    assert len(keyboard) == 3
    assert len(keyboard[0]) == 1
    assert keyboard[0][0].text == "Url"
    assert keyboard[0][0].url == "https://test.com"


@pytest.mark.asyncio
async def test_render_list_group_with_callback_button(
    mock_manager: DialogManager,
) -> None:
    list_group = ListGroup(
        Button(Format("Callback {item}"), "button"),
        id="list",
        items=["a", "b", "c"],
        item_id_getter=lambda item: item,
    )

    keyboard = await list_group.render_keyboard(data={}, manager=mock_manager)

    assert len(keyboard) == 3

    assert len(keyboard[0]) == 1
    assert keyboard[0][0].text == "Callback a"
    assert keyboard[0][0].payload == "list:a:button"

    assert len(keyboard[2]) == 1
    assert keyboard[1][0].text == "Callback b"
    assert keyboard[1][0].payload == "list:b:button"

    assert len(keyboard[2]) == 1
    assert keyboard[2][0].text == "Callback c"
    assert keyboard[2][0].payload == "list:c:button"
