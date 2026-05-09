from .user import User
from .state import State

class Users:
    def __init__(self, state: State):
        self._state = state

    async def fetch(self, user_id: int) -> User:
        return User(self._state, await self._state.request(
            "GET",
            f"users/{user_id}"
        ))
