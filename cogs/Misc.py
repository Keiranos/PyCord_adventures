import discord
from discord.ext import commands


class Misc(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @discord.slash_command(name="ping")
    async def ping(self, ctx: discord.ApplicationContext):
        msg = f"Pong!\nDiscord latency: {self.bot.latency * 1000:.0f}ms"
        await ctx.respond(content=msg, ephemeral=False)


def setup(bot: commands.Bot):
    bot.add_cog(Misc(bot))
