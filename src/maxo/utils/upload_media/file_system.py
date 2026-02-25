import os
from pathlib import Path

from anyio import open_file

from maxo.enums import UploadType
from maxo.utils.upload_media.base import InputFile


class FSInputFile(InputFile):
    __slots__ = ("_file_name", "_path", "_type")

    def __init__(
        self,
        path: str | Path,
        type: UploadType,
        file_name: str | None = None,
    ) -> None:
        if file_name is None:
            file_name = os.path.basename(path)  # noqa: PTH119

        self._path = path
        self._type = type
        self._file_name = file_name

    @property
    def path(self) -> str | Path:
        return self._path

    @property
    def type(self) -> UploadType:
        return self._type

    @property
    def file_name(self) -> str:
        return self._file_name

    @classmethod
    def image(cls, path: str | Path, file_name: str | None = None) -> "FSInputFile":
        return cls(path=path, file_name=file_name, type=UploadType.IMAGE)

    @classmethod
    def video(cls, path: str | Path, file_name: str | None = None) -> "FSInputFile":
        return cls(path=path, file_name=file_name, type=UploadType.VIDEO)

    @classmethod
    def audio(cls, path: str | Path, file_name: str | None = None) -> "FSInputFile":
        return cls(path=path, file_name=file_name, type=UploadType.AUDIO)

    @classmethod
    def file(cls, path: str | Path, file_name: str | None = None) -> "FSInputFile":
        return cls(path=path, file_name=file_name, type=UploadType.FILE)

    async def read(self) -> bytes:
        async with await open_file(self._path, "rb") as file:
            return await file.read()
