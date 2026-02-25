import pytest

from maxo.errors.base import MaxoError


def test_maxo_error() -> None:
    class MyError(MaxoError):
        foo: int
        bar: str

    err = MyError(1, bar="2")

    assert err.foo == 1
    assert err.bar == "2"

    with pytest.raises(TypeError):
        MyError(foo=1)  # type: ignore[call-arg]

    with pytest.raises(TypeError):
        MyError(bar="2")  # type: ignore[call-arg]

    with pytest.raises(TypeError):
        MyError(1, "2", "3")  # type: ignore[call-arg]
