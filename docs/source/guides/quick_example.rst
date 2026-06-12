Quick Example
=============

Now after setting up our environment, we can start building a basic bot.

.. code-block:: python

    import mizuki
    
    bot = mizuki.Bot(
        intents=mizuki.IntentFlags.standard()
    )
    
    @bot.setup()
    async def setup():
        commands = await bot.commands.sync_all()
        print(f"Synced {len(commands)} commands!")
    
    @bot.command(
        name="ping",
        description="Pings the bot!"
    )
    async def ping(interaction: mizuki.Interaction):
        await interaction.response.send_response("Pong!")

    bot.run("TOKEN-HERE")
    
There's a lot of things going on here, so let's walk through it.

The first line just imports the library.

.. code-block:: python

    import mizuki
    

Next up we create an instance of a Bot with :class:`mizuki.Bot <mizuki.bot.Bot>` with the parameter intents. :class:`mizuki.IntentFlags <mizuki.flags.IntentFlags>` define the events which your bot gets from Discord. Here we use :meth:`mizuki.IntentFlags.standard() <mizuki.flags.IntentFlags.standard>` to enable all non-privileged intents. You can learn more about intents here placeholderlinkwow.

.. code-block:: python

    bot = mizuki.Bot(
        intents=mizuki.IntentFlags.standard()
    )
    

We use the :meth:`@Bot.setup() <mizuki.bot.Bot.setup>` decorator to make a setup hook. This function will run right alongside the connection of the gateway.

Here we call the :meth:`bot.commands.sync_all() <mizuki.managers.command.CommandManager.sync_all>` method to sync all of our commands registered with :meth:`@Bot.command <mizuki.bot.Bot.command>` to Discord. The method here also returns a list of the Application Commands we just synced.

.. code-block:: python

    @bot.setup()
    async def setup():
        commands = await bot.commands.sync_all()
        print(f"Synced {len(commands)} commands!")
        

.. note::
    
    The gateway connection is not guaranteed to be ready in this function! Look to :meth:`@Bot.listen() <mizuki.bot.Bot.listen>` with the :attr:`Event.READY <mizuki.enums.event_dispatch.Event.READY>` for that.
    

We use the :meth:`@Bot.command() <mizuki.bot.Bot.command()>` decorator with the name and description parameters to define how the command will appear in Discord.

The method we apply the decorator to is our "callback" function, it will be executed when someone uses the command in Discord.

Every command callback receives an :class:`Interaction <mizuki.objects.interaction.Interaction>` as its first parameter. If the callback is defined within a class, self is passed first and the :class:`Interaction <mizuki.objects.interaction.Interaction>` becomes the second parameter.

:attr:`interaction.response <mizuki.objects.interaction.Interaction.response>` is our :class:`ResponseHandler <mizuki.objects.interaction.ResponseHandler>`, which we will be using to send, followup, edit and delete our responses. :meth:`ResponseHandler.send_response() <mizuki.objects.interaction.ResponseHandler.send_response>` is used to send the first intial response to the command.

.. code-block:: python

    @bot.command(
        name="ping",
        description="Pings the bot!"
    )
    async def ping(interaction: mizuki.Interaction):
        await interaction.response.send_response("Pong!")

        
.. important::
    
    All application commands must be responded or deferred to in under 3 seconds. If an interaction is not responded or deferred, then the interaction is invalidated.
    
    After acknowledging the interaction, you can keep responding with :meth:`ResponseHandler.send_followup() <mizuki.objects.interaction.ResponseHandler.send_followup>` until the interaction token is invalidated in 15 minutes.
    
    
Finally, we run the bot using :meth:`Bot.run() <mizuki.bot.Bot.run>` with the token parameter.

.. code-block:: python

    bot.run("TOKEN-HERE")
    
    
You have made your first Discord bot!