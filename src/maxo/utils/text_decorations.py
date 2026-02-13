# Source:
# https://github.com/aiogram/aiogram/blob/dev-3.x/aiogram/utils/text_decorations.py

import html
import re
from abc import ABC, abstractmethod
from collections.abc import Generator
from re import Pattern
from typing import cast

from maxo.enums import MarkupElementType
from maxo.types.markup_elements import MarkupElements
from maxo.types.user_mention_markup import UserMentionMarkup

__all__ = (
    "HtmlDecoration",
    "MarkdownDecoration",
    "TextDecoration",
    "add_surrogates",
    "html_decoration",
    "markdown_decoration",
    "remove_surrogates",
)


def add_surrogates(text: str) -> bytes:
    return text.encode("utf-16-le")


def remove_surrogates(text: bytes) -> str:
    return text.decode("utf-16-le")


class TextDecoration(ABC):
    def apply_entity(self, entity: MarkupElements, text: str) -> str:
        if entity.type in {
            MarkupElementType.EMPHASIZED,
            MarkupElementType.MONOSPACED,
            MarkupElementType.STRIKETHROUGH,
            MarkupElementType.STRONG,
            MarkupElementType.UNDERLINE,
        }:
            return cast(str, getattr(self, entity.type)(value=text))

        if entity.type == MarkupElementType.USER_MENTION:

            entity: UserMentionMarkup

            if entity.user_link:
                return entity.user_link
            return self.link(value=text, link=f"max://user/{entity.user_id}")

        if entity.type == MarkupElementType.LINK:
            return self.link(value=text, link=cast(str, entity.url))

        # This case is not possible because of `if` above,
        # but if any new entity is added to API it will be here too
        return self.quote(text)

    def unparse(self, text: str, entities: list[MarkupElements] | None = None) -> str:
        return "".join(
            self._unparse_entities(
                add_surrogates(text),
                sorted(entities, key=lambda item: item.offset) if entities else [],
            ),
        )

    def _unparse_entities(
        self,
        text: bytes,
        entities: list[MarkupElements],
        offset: int | None = None,
        length: int | None = None,
    ) -> Generator[str, None, None]:
        if offset is None:
            offset = 0
        length = length or len(text)

        for index, entity in enumerate(entities):
            if entity.offset * 2 < offset:
                continue
            if entity.offset * 2 > offset:
                yield self.quote(remove_surrogates(text[offset : entity.offset * 2]))
            start = entity.offset * 2
            offset = entity.offset * 2 + entity.length * 2

            sub_entities = list(
                filter(lambda e: e.offset * 2 < (offset or 0), entities[index + 1 :]),
            )
            yield self.apply_entity(
                entity,
                "".join(
                    self._unparse_entities(
                        text,
                        sub_entities,
                        offset=start,
                        length=offset,
                    ),
                ),
            )

        if offset < length:
            yield self.quote(remove_surrogates(text[offset:length]))

    @abstractmethod
    def emphasized(self, value: str) -> str:
        pass

    @abstractmethod
    def link(self, value: str, link: str) -> str:
        pass

    @abstractmethod
    def monospaced(self, value: str) -> str:
        pass

    @abstractmethod
    def strikethrough(self, value: str) -> str:
        pass

    @abstractmethod
    def strong(self, value: str) -> str:
        pass

    @abstractmethod
    def underline(self, value: str) -> str:
        pass

    @abstractmethod
    def quote(self, value: str) -> str:
        pass


class HtmlDecoration(TextDecoration):
    STRONG_TAG = "b"
    EMPHASIZED_TAG = "i"
    UNDERLINE_TAG = "u"
    STRIKETHROUGH_TAG = "s"
    MONOSPACED_TAG = "pre"

    def emphasized(self, value: str) -> str:
        return f"<{self.EMPHASIZED_TAG}>{value}</{self.EMPHASIZED_TAG}>"

    def link(self, value: str, link: str) -> str:
        return f'<a href="{link}">{value}</a>'

    def monospaced(self, value: str) -> str:
        return f"<{self.MONOSPACED_TAG}>{value}</{self.MONOSPACED_TAG}>"

    def strikethrough(self, value: str) -> str:
        return f"<{self.STRIKETHROUGH_TAG}>{value}</{self.STRIKETHROUGH_TAG}>"

    def strong(self, value: str) -> str:
        return f"<{self.STRONG_TAG}>{value}</{self.STRONG_TAG}>"

    def underline(self, value: str) -> str:
        return f"<{self.UNDERLINE_TAG}>{value}</{self.UNDERLINE_TAG}>"

    def quote(self, value: str) -> str:
        return html.escape(value, quote=False)


class MarkdownDecoration(TextDecoration):
    MARKDOWN_QUOTE_PATTERN: Pattern[str] = re.compile(r"([_*\[\]()~`>#+\-=|{}.!\\])")

    def emphasized(self, value: str) -> str:
        return f"_{value}_"

    def link(self, value: str, link: str) -> str:
        return f"[{value}]({link})"

    def monospaced(self, value: str) -> str:
        return f"`{value}`"

    def strikethrough(self, value: str) -> str:
        return f"~~{value}~~"

    def strong(self, value: str) -> str:
        return f"**{value}**"

    def underline(self, value: str) -> str:
        return f"++{value}++"

    def quote(self, value: str) -> str:
        return re.sub(pattern=self.MARKDOWN_QUOTE_PATTERN, repl=r"\\\1", string=value)


html_decoration = HtmlDecoration()
markdown_decoration = MarkdownDecoration()
