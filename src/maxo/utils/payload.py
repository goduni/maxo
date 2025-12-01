from base64 import urlsafe_b64decode, urlsafe_b64encode
from collections.abc import Callable


def encode_payload(
    payload: str,
    encoder: Callable[[bytes], bytes] | None = None,
) -> str:
    if not isinstance(payload, str):
        payload = str(payload)

    payload_bytes = payload.encode("utf-8")
    if encoder is not None:
        payload_bytes = encoder(payload_bytes)

    return _encode_b64(payload_bytes)


def decode_payload(
    payload: str,
    decoder: Callable[[bytes], bytes] | None = None,
) -> str:
    original_payload = _decode_b64(payload)

    if decoder is None:
        return original_payload.decode()

    return decoder(original_payload).decode()


def _encode_b64(payload: bytes) -> str:
    bytes_payload: bytes = urlsafe_b64encode(payload)
    str_payload = bytes_payload.decode()
    return str_payload.replace("=", "")


def _decode_b64(payload: str) -> bytes:
    payload += "=" * (4 - len(payload) % 4)
    return urlsafe_b64decode(payload.encode())
