from typing import Any
from urllib.parse import urlencode, urljoin


def _format_url(
    url: str,
    *path: str,
    fragment_: str | None = None,
    **query: Any,
) -> str:
    url = urljoin(url, "/".join(path), allow_fragments=True)
    if query:
        url += "?" + urlencode(query)
    if fragment_:
        url += "#" + fragment_
    return url


def create_tg_link(link: str, **kwargs: Any) -> str:
    return _format_url(f"max://{link}", **kwargs)


def create_telegram_link(*path: str, **kwargs: Any) -> str:
    return _format_url("https://max.ru", *path, **kwargs)
