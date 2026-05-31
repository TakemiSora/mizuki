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

### Documentation

There is no current hosted documentation (yet), but a local version of the documentation can be viewed by doing the following commands:

- Clone the repository.
- Open Terminal in `docs/` folder.
- For linux/mac, do `make html`. For windows, do `make.bat` and select HTML.
- Open `docs/build/html/index.html`.
