# Mizuki

A modern async-based discord API wrapper written for Python. Currently in early development, not meant to be used in production as of now.  
I aim for this library to closely mirror the discord API.

## Installation

```
pip install mizuki
```

## Quick Example

```python
import mizuki

bot = mizuki.Bot(
     intents=mizuki.IntentFlags.standard()
)

@bot.setup()
async def setup():
    commands = await bot.commands.sync_all()
    print(f"Synced {len(commands)} commands!")

@bot.command(name="ping", description="Send a ping to the bot")
async def ping(interaction: mizuki.Interaction):
    await interaction.response.send_response("Pong!")

bot.run("TOKEN-HERE")
```

## Documentation

Documentation can be viewed [here](https://mizuki.readthedocs.io/).
