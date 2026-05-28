__all__ = (
    "HTTPException",
    "GatewayError",
    "NotFound",
    "Forbidden",
    "Unauthorized",
    "ImproperToken",
    "UnknownChannelType"
)

class HTTPException(Exception):
    def __init__(self, status: int, message: str):
        self.status = status
        self.message = message
        super().__init__(f"HTTP {status}: {message}")

class GatewayError(Exception):
    def __init__(self, status: int, message: str):
        self.status = status
        self.message = message
        super().__init__(f"Gateway Closed with {status}: {message}")

class NotFound(HTTPException):
    pass

class Forbidden(HTTPException):
    pass

class Unauthorized(HTTPException):
    pass

class ImproperToken(HTTPException):
    pass

class UnknownChannelType(Exception):
    pass
        
class UnknownInteractionType(Exception):
    pass