from collections.abc import MutableMapping
from typing import Any, NewType

Ctx = NewType("Ctx", MutableMapping[str, Any])
