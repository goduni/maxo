import hashlib
import hmac
from typing import Any


def check_signature(token: str, hash: str, **kwargs: Any) -> bool:
    secret = hashlib.sha256(token.encode("utf-8"))
    check_string = "\n".join(f"{k}={kwargs[k]}" for k in sorted(kwargs))
    hmac_string = hmac.new(
        secret.digest(),
        check_string.encode("utf-8"),
        digestmod=hashlib.sha256,
    ).hexdigest()
    return hmac_string == hash


def check_integrity(token: str, data: dict[str, Any]) -> bool:
    return check_signature(token, **data)
