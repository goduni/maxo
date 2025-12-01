import hashlib
import hmac
import json
from collections.abc import Callable
from operator import itemgetter
from typing import Any
from urllib.parse import parse_qsl

from maxo.types.base import MaxoType


class WebAppChat(MaxoType):
    id: int
    type: str


class WebAppUser(MaxoType):
    id: int
    first_name: str
    last_name: str | None = None
    username: str | None = None
    language_code: str | None = None
    photo_url: str | None = None


class WebAppInitData(MaxoType):
    ip: str | None = None
    query_id: str | None = None
    chat: WebAppChat
    user: WebAppUser
    auth_date: str | None = None
    hash: str
    start_param: str | None = None


def check_webapp_signature(token: str, init_data: str) -> bool:
    try:
        parsed_data = dict(parse_qsl(init_data, strict_parsing=True))
    except ValueError:  # pragma: no cover
        # Init data is not a valid query string
        return False
    if "hash" not in parsed_data:
        # Hash is not present in init data
        return False
    hash_ = parsed_data.pop("hash")

    data_check_string = "\n".join(
        f"{k}={v}" for k, v in sorted(parsed_data.items(), key=itemgetter(0))
    )
    secret_key = hmac.new(
        key=b"WebAppData",
        msg=token.encode(),
        digestmod=hashlib.sha256,
    )
    calculated_hash = hmac.new(
        key=secret_key.digest(),
        msg=data_check_string.encode(),
        digestmod=hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(calculated_hash, hash_)


def parse_webapp_init_data(
    init_data: str,
    *,
    loads: Callable[..., Any] = json.loads,
) -> WebAppInitData:
    result: dict[str, Any] = {}
    for key, value in parse_qsl(init_data):
        if (value.startswith("[") and value.endswith("]")) or (
            value.startswith("{") and value.endswith("}")
        ):
            value = loads(value)
        result[key] = value

    chat: dict[str, Any] = result.pop("chat", {})
    user: dict[str, Any] = result.pop("user", {})

    return WebAppInitData(**result, chat=WebAppChat(**chat), user=WebAppUser(**user))


def safe_parse_webapp_init_data(
    token: str,
    init_data: str,
    *,
    loads: Callable[..., Any] = json.loads,
) -> WebAppInitData:
    if check_webapp_signature(token, init_data):
        return parse_webapp_init_data(init_data, loads=loads)
    raise ValueError("Invalid init data signature")
