from maxo import Router
from maxo.routing.filters import CommandStart
from maxo.routing.updates import MessageCreated
from maxo.utils.facades import MessageCreatedFacade

start_router = Router(__name__)


@start_router.message_created(CommandStart())
async def start_handler(
    message: MessageCreated,
    facade: MessageCreatedFacade,
) -> None:
    await facade.answer_text(
        "Привет! Я бот из нескольких модулей. Напиши что-нибудь — отвечу эхом.",
    )
