from typing import Any

from maxo.errors.base import MaxoError


class MaxBotApiError(MaxoError):
    """Сервер возвращает это, если возникло исключение при вашем запросе."""

    code: str
    error: str
    message: str
    raw_data: Any = None


class MaxBotBadRequestError(MaxBotApiError): ...


class MaxBotForbiddenError(MaxBotApiError): ...


class MaxBotUnauthorizedError(MaxBotApiError): ...


class MaxBotNotFoundError(MaxBotApiError): ...


class MaxBotMethodNotAllowedError(MaxBotApiError): ...


class MaxBotUnsupportedMediaTypeError(MaxBotApiError): ...


class MaxBotTooManyRequestsError(MaxBotApiError): ...


class MaxBotUnknownServerError(MaxBotApiError): ...


class MaxBotServiceUnavailableError(MaxBotApiError): ...


class RetvalReturnedServerException(MaxoError): ...
