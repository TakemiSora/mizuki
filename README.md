# Mizuki

A modern async-based discord API wrapper written for Python. Currently in early development, not meant to be used in production as of now.  
I aim for this library to closely mirror the discord API.

## Installation

```
pip install git+https://github.com/TakemiSora/mizuki
```

## Quick Example

```python
import mizuki

bot = mizuki.Bot(
     intents=mizuki.IntentFlags.standard()
)

@bot.command(name="ping", description="Send a ping to the bot")
async def ping(interaction: mizuki.Interaction):
    await interaction.response.send_response("Pong!")

bot.run("TOKEN-HERE")
```

## Documentation

There is no current hosted documentation (yet), but a local version of the documentation can be viewed by doing the following steps:

```
# 1. Clone the repository
git clone https://github.com/TakemiSora/mizuki

# 2. Navigate into the docs directory
cd mizuki/docs/

# 3. Build the HTML documentation
## Linux/Mac
make html

## Windows
make.bat html

# 4. Start a local server to view them
cd build/html
python -m http.server 8000
```

Then open `https://localhost:8000/` to open the documentation.