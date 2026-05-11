class HTTPException(Exception):
    def __init__(self, status: int, message: str):
        self.status = status
        self.message = message
        super().__init__(f"HTTP {status}: {message}")

class NotFound(HTTPException):
    pass

class Forbidden(HTTPException):
    pass

class Unauthorized(HTTPException):
    pass

class ImproperToken(HTTPException):
    pass