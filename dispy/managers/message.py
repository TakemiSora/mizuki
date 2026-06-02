from ._types import BaseManager
from ..http import Path
from ..objects.message import Message

__all__ = (
    "MessageManager",
)

class MessageManager(BaseManager):
    """"
    Manager used to fetch :class:`Message <dispy.objects.message.Message>` objects.
    """

    __slots__ = ()

    def get(self, message_id: int) -> Message | None:
        """
        Attempts to fetch a :class:`Message <dispy.objects.message.Message>` from the internal cache of the bot.
        
        Parameters
        ----------
        message_id: :class:`int`
            The message_id of the message to fetch.
            
        Returns
        -------
        :class:`Message <dispy.objects.message.Message>`
            The Messsge received from the cache.
        :class:`None`
            Could not find the User object in the internal cache.
        """
        return self._cache_storage.get_message(message_id)

    async def fetch(self, channel_id: int, message_id: int) -> Message:
        """
        Attempts to fetch a :class:`Message <dispy.objects.message.Message>` from the Discord API.
        
        Parameters
        ----------
        message_id: :class:`int`
            The message_id of the message to fetch.
            
        Returns
        -------
        :class:`Message <dispy.objects.message.Message>`
            The Message object recieved from Discord API.
            
        Raises
        ------
        :class:`NotFound`
            Could not find an message with that ID.
        :class:`Forbidden`
            You are not allowed to fetch that message.
        :class:`HTTPException`
            A HTTP error occured.
        """
        return self._cache_storage.update_messages(
            Message(await self._http.request(
                Path(
                    "GET",
                    "channels/{channel_id}/messages/{message_id}",
                    channel_id=channel_id,
                    message_id=message_id
            )))
        )

    async def get_or_fetch(self, channel_id: int, message_id: int) -> Message:
        """
        A couroutine function that attempts to fetch a :class:`Message <dispy.objects.message.Message>` from internal cache and if not present, makes an API call to discord.
        
        Parameters
        ----------
        message_id: :class:`int`
            The message_id of the message to fetch.
            
        Returns
        -------
        :class:`Message <dispy.objects.message.Message>`
            The Message object recieved from Discord API or cache.
            
        Raises
        ------
        :class:`NotFound`
            Could not find an message with that ID.
        :class:`Forbidden`
            You are not allowed to fetch that message.
        :class:`HTTPException`
            A HTTP error occured.
        """
        return self.get(message_id) or await self.fetch(channel_id, message_id)