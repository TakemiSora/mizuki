# Dispy

A modern async-based discord API wrapper written for Python. Currently in early development, not meant to be used in production as of now.  
I aim for this library to closely mirror the discord API.

### Quick Example

```python
import dispy

bot = dispy.Bot(
    "TOKEN-HERE",
     intents=dispy.IntentFlags.standard()
)

bot.run()
```
