import pytest
from magic_filter import F

from maxo.integrations.magic_filter import MagicData, MagicFilter


@pytest.mark.asyncio
async def test_magic_filter_custom_cast() -> None:
    magic_filter = MagicFilter(F["item"].cast(str), result_key="result")

    ctx = {}
    result = await magic_filter({"item": 42}, ctx)

    assert result is True
    assert "result" in ctx
    assert ctx["result"] == "42"
    assert isinstance(ctx["result"], str)


@pytest.mark.asyncio
async def test_magic_data_custom_cast() -> None:
    magic_data = MagicData(F["item"].cast(str), result_key="result")

    ctx = {"item": 42}
    result = await magic_data(None, ctx)

    assert result is True
    assert "result" in ctx
    assert ctx["result"] == "42"
    assert isinstance(ctx["result"], str)
