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
    "InteractionNotResponded"
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

    status: int
    "The error code of the HTTP error."

    message: str
    "The message of the HTTP error."

    def __init__(self, status: int, message: str):
        self.status = status
        self.message = message
        super().__init__(f"HTTP {status}: {message}")

class GatewayError(Exception):
    """
    Raised when a Gateway error occurs.

    Parameters
    ----------
    status : :class:`int`
        The error code of the HTTP error.
    message : :class:`int`
        The message of the HTTP error
    """

    status: int
    "The error code of the HTTP error."

    message: str
    "The message of the HTTP error."

    def __init__(self, status: int, message: str):
        self.status = status
        self.message = message
        super().__init__(f"Gateway Closed with {status}: {message}")

class NotFound(HTTPException):
    "Raised when the resource you tried to access was not found."

class Forbidden(HTTPException):
    "Raised when you are forbidden from the resource you tried to access."

class Unauthorized(HTTPException):
    "Raised when the server could not authenticate your identity."

class ImproperToken(HTTPException):
    "Raised when an improper token was passed when calling :meth:`Bot.start() <dispy.bot.Bot.start>`."
    
class UnknownChannelType(Exception):
    "Raised when the channel parser could not parse the channel you received."
        
class UnknownInteractionType(Exception):
    "Raised when the interaction parser could not parse the interaction you received."

class InteractionResponded(Exception):
    "Raised when you attempt to respond to an already responded interaction."

class InteractionNotResponded(Exception):
    "Raised when you attempt to send a followup to an interaction you haven't responded to yet."

class _RateLimitedRetry(Exception):
    def __init__(self, data: dict[str, Any], retry_after: float, limit_scope: str | None, bucket_id: str | None):
        self.data = data
        self.retry_after = retry_after
        self.limit_scope = limit_scope
        self.bucket_id = bucket_id