import discord
from discord.ext import commands
import asyncio
import os
from dotenv import load_dotenv
from os import getenv
from config import PREFIX

load_dotenv()


class Bot(commands.Bot):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


intents = discord.Intents.all()
allowed_mentions = discord.AllowedMentions(everyone=False)


bot = Bot(command_prefix=commands.when_mentioned_or(PREFIX), owner_id=114352655857483782, intents=intents,
          allowed_mentions=allowed_mentions)

bot.remove_command("help")


# Load cogs
for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        print("Loading: cogs." + filename[:-3])
        bot.load_extension("cogs." + filename[:-3])


@bot.event
async def on_ready():
    startup = bot.user.name + " is running"
    print(startup)
    print("-" * len(startup))

bot.run(getenv("TOKEN"))

