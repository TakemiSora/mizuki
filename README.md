# Dispy

A modern async-based discord API wrapper written for Python. Currently in early development, not meant to be used in production as of now.  
I aim for this library to closely mirror the discord API.

## Installation

Currently the package is not published, but you can install it locally via following steps:

- Clone this repository.
- Open Terminal in the root folder (The folder that contains the `pyproject.toml`).
- Do `pip install -e .`.

> [!NOTE]
> The -e flag is used so you can do `git pull` to update the library.

## Quick Example

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

## Documentation

There is no current hosted documentation (yet), but a local version of the documentation can be viewed by doing the following steps:

- Clone the repository.
- Open Terminal in `docs/` folder.
- For linux/mac, do `make html`. For windows, do `make.bat` and select HTML.
- Open `docs/build/html/index.html`.
