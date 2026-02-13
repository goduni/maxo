import asyncio
from collections.abc import Sequence

from unihttp.http import UploadFile

from maxo import loggers
from maxo.enums import UploadType
from maxo.errors.api import RetvalReturnedServerException
from maxo.omit import is_defined
from maxo.types import (
    AttachmentsRequests,
    AudioAttachmentRequest,
    FileAttachmentRequest,
    InlineButtons,
    InlineKeyboardAttachmentRequest,
    InlineKeyboardAttachmentRequestPayload,
    MediaAttachmentsRequests,
    PhotoAttachmentRequest,
    UploadMediaResult,
    VideoAttachmentRequest,
)
from maxo.utils.facades.methods.bot import BotMethodsFacade
from maxo.utils.upload_media import InputFile


class AttachmentsFacade(BotMethodsFacade):
    async def _build_attachments(
        self,
        base: Sequence[AttachmentsRequests],
        keyboard: Sequence[Sequence[InlineButtons]] | None = None,
        media: Sequence[InputFile] | None = None,
    ) -> Sequence[AttachmentsRequests]:
        attachments = list(base)

        if keyboard is not None:
            attachments.append(
                InlineKeyboardAttachmentRequest(
                    payload=InlineKeyboardAttachmentRequestPayload(buttons=keyboard),
                ),
            )

        if media:
            # TODO: Исправить костыль со сном, https://github.com/K1rL3s/maxo/issues/10
            # maxo.errors.api.MaxBotBadRequestError:
            # ('attachment.not.ready',
            # 'Key: errors.process.attachment.file.not.processed')
            attachments.extend(await self._build_media_attachments(media))
            await asyncio.sleep(0.5)

        return attachments

    async def _build_media_attachments(
        self,
        media: Sequence[InputFile],
    ) -> Sequence[MediaAttachmentsRequests]:
        attachments: list[MediaAttachmentsRequests] = []

        result = await asyncio.gather(
            *(self.upload_media(upload_media) for upload_media in media),
        )

        for type_, token in result:
            match type_:
                case UploadType.FILE:
                    attachments.append(FileAttachmentRequest.factory(token))
                case UploadType.AUDIO:
                    attachments.append(AudioAttachmentRequest.factory(token))
                case UploadType.VIDEO:
                    attachments.append(VideoAttachmentRequest.factory(token))
                case UploadType.IMAGE:
                    attachments.append(PhotoAttachmentRequest.factory(token=token))
                case _:
                    loggers.utils.warning("Received unknown attachment type: %s", type_)

        return attachments

    async def upload_media(self, media: InputFile) -> tuple[UploadType, str]:
        result = await self.bot.get_upload_url(type=media.type)

        upload_result: UploadMediaResult | None
        try:
            upload_result = await self.bot.upload_media(
                upload_url=result.url,
                file=UploadFile(
                    file=await media.read(),
                    filename=media.file_name,
                ),
            )
        except RetvalReturnedServerException:
            upload_result = None

        token: str
        if is_defined(result.token):
            token = result.token
        elif upload_result is not None:
            token = upload_result.last_token
        else:
            raise RuntimeError("Could not get upload token")

        return media.type, token
