import asyncio
import aiohttp
from discord import Game
from discord.ext.commands import Bot
BOT_PREFIX = ("?", "!")
client = Bot(command_prefix=BOT_PREFIX)
TOKEN = "this aint my token"


@client.event
async def on_ready():
    print("Ready to record!")

@client.event
async def on_message(message):
    if message.author == client.user:
        return
      
    #Insert your code here




client.run(TOKEN)
