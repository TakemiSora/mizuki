import aiohttp
from typing import Any

class State:
    def __init__(self, session: aiohttp.ClientSession | None = None):
        self.session = session

    async def request(self, method: str, url: str) -> Any:
        async with self.session.request(method, url) as r:
            data = await r.json()

            if r.status >= 400:
                raise Exception(data)
            
        return data