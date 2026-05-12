from .user import User
from .http import State, Path

class Users:
    __slots__ = (
        "_state"
    )
    
    def __init__(self, state: State):
        self._state = state

    async def fetch(self, user_id: int) -> User:
        return User(await self._state.request(
            Path("GET", "users/{user_id}", user_id=user_id)
        ))