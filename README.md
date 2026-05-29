# Dispy

A modern async-based discord API wrapper written for Python. Currently in early development, not meant to be used in production as of now.  
I aim for this library to closely mirror the discord API.

### Quick Example

```python
import dispy

bot = dispy.Bot(
     intents=dispy.IntentFlags.standard()
)

@bot.command(name="ping", description="Send a ping to the bot")
async def ping(interaction: dispy.Interaction):
    await interaction.response.send_response("Pong!")

bot.run("TOKEN-HERE")
```
