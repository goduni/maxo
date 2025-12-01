from dataclasses import field
from re import Match

from maxo.types.base import MaxoType


class CommandObject(MaxoType):
    prefix: str = "/"
    command: str = ""
    mention: str | None = None
    args: str | None = field(repr=False, default=None)
    regexp_match: Match[str] | None = field(repr=False, default=None)

    @property
    def mentioned(self) -> bool:
        return bool(self.mention)

    @property
    def text(self) -> str:
        line = self.prefix + self.command
        if self.mention:
            line += "@" + self.mention
        if self.args:
            line += " " + self.args
        return line
