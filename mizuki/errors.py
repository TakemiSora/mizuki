from typing import Any

__all__ = (
    "HTTPException",
    "GatewayError",
    "NotFound",
    "Forbidden",
    "Unauthorized",
    "ImproperToken",
    "UnknownChannelType",
    "InteractionResponded",
    "InteractionNotResponded",
)


class HTTPException(Exception):
    """
    Raised when an HTTP error occurs.

    Parameters
    ----------
    status : :class:`int`
        The error code of the HTTP error.
    message : :class:`int`
        The message of the HTTP error
    """

    status: int = 0
    "The error code of the HTTP error."

    message: str
    "The message of the HTTP error."

    def __init__(self, message: str):
        self.message = message
        super().__init__(f"HTTP {self.status}: {message}")


class GatewayError(Exception):
    """
    Raised when a Gateway error occurs.

    Parameters
    ----------
    status : :class:`int`
        The error code of the Gateway error.
    message : :class:`int`
        The message of the Gateway error
    """

    status: int
    "The error code of the Gateway error."

    message: str
    "The message of the Gateway error."

    def __init__(self, status: int, message: str):
        self.status = status
        self.message = message
        super().__init__(f"Gateway Closed with {status}: {message}")


class NotFound(HTTPException):
    "Raised when the resource you tried to access was not found."

    status = 404


class Forbidden(HTTPException):
    "Raised when you are forbidden from the resource you tried to access."

    status = 403


class Unauthorized(HTTPException):
    "Raised when the server could not authenticate your identity."

    status = 401


class ImproperToken(HTTPException):
    "Raised when an improper token was passed when calling :meth:`Bot.start() <mizuki.bot.Bot.start>`."

    status = 401


class BadRequest(HTTPException):
    "Raised when you make an invalid request."

    status = 400

    def __init__(self, data: dict[str, Any]) -> None:
        super().__init__(
            f"Error Code {data['code']}: {BadRequest.error_parser(data['errors'])}"
        )

    @staticmethod
    def error_parser(
        current_data: dict[str, Any], path_traversed: list[str] | None = None
    ) -> str:
        if not path_traversed:
            path_traversed = []

        for key, value in current_data.items():
            if key == "_errors":
                return f"{'.'.join(path_traversed)}: {', '.join(error['message'] for error in value)}"
            path_traversed.append(key)
            return BadRequest.error_parser(value, path_traversed)

        return "Could not parse the BadRequest error."


class UnknownChannelType(Exception):
    "Raised when the channel parser could not parse the channel you received."


class UnknownInteractionType(Exception):
    "Raised when the interaction parser could not parse the interaction you received."


class InteractionResponded(Exception):
    "Raised when you attempt to respond to an already responded interaction."


class InteractionNotResponded(Exception):
    "Raised when you attempt to send a followup to an interaction you haven't responded to yet."


class _RateLimitedRetry(Exception):
    def __init__(
        self,
        data: dict[str, Any],
        retry_after: float,
        limit_scope: str | None,
        bucket_id: str | None,
    ):
        self.data = data
        self.retry_after = retry_after
        self.limit_scope = limit_scope
        self.bucket_id = bucket_id
