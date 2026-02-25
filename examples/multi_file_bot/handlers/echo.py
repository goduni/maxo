from maxo import Router
from maxo.routing.updates import MessageCreated
from maxo.utils.facades import MessageCreatedFacade

echo_router = Router(__name__)


@echo_router.message_created()
async def echo_handler(
    message: MessageCreated,
    facade: MessageCreatedFacade,
) -> None:
    text = message.message.body.text or "Текста нет"
    await facade.answer_text(text)
