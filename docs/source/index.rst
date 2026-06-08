.. mizuki documentation master file, created by
   sphinx-quickstart on Sun May 31 07:35:38 2026.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

mizuki Documentation
===================

A modern async-based discord API wrapper written for Python. Currently in early development, not meant to be used in production as of now.

Quick Example
-------------

.. code-block:: python
   
   import mizuki

   bot = mizuki.Bot(
      intents=mizuki.IntentFlags.standard()
   )

   @bot.command(
      name="ping",
      description="Pings the bot!"
   )
   async def ping(interaction: mizuki.Interaction):
      await interaction.response.send_message("Pong!")

   bot.run("TOKEN-HERE")

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   modules